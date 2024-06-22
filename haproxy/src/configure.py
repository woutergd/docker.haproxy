import os
from string import Template
import subprocess

################################################################################
# INIT
################################################################################

COOKIES_ENABLED = (os.environ.get('COOKIES_ENABLED', 'false').lower() == "true")
COOKIES_NAME = os.environ.get('COOKIES_NAME','SRV_ID')
COOKIES_PARAMS = os.environ.get('COOKIES_PARAMS','')
PROXY_PROTOCOL_ENABLED = (os.environ.get('PROXY_PROTOCOL_ENABLED', 'false').lower() == "true")
STATS_PORT = os.environ.get('STATS_PORT', '1936')
STATS_AUTH = os.environ.get('STATS_AUTH', 'admin:admin')
LOGGING = os.environ.get('LOGGING', '127.0.0.1')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'notice')
TIMEOUT_CONNECT = os.environ.get('TIMEOUT_CONNECT', '5000')
TIMEOUT_CLIENT = os.environ.get('TIMEOUT_CLIENT', '50000')
TIMEOUT_SERVER = os.environ.get('TIMEOUT_SERVER', '50000')

# Read these variables, as these are the defaults for others
FRONTEND_POOLS = int(os.environ.get("FRONTEND_POOLS", 1))
BACKEND_MODE = os.environ.get("BACKEND_MODE", "http")

# Frontend variables
FRONTEND_MODE = os.environ.get("FRONTEND_MODE", BACKEND_MODE)

# Backend variables
BACKEND_POOLS = int(os.environ.get("BACKEND_POOLS", FRONTEND_POOLS))
BACKEND_PORT = os.environ.get("BACKEND_PORT", "5000")
BACKEND_BALANCE = os.environ.get('BACKEND_BALANCE', 'roundrobin')
BACKEND_DEFAULT_SERVER = os.environ.get("BACKEND_DEFAULT_SERVER", "inter 2s fastinter 2s downinter 2s fall 3 rise 2")

# Backend Http checks
HTTPCHK_METHOD = os.environ.get('HTTPCHK_METHOD', 'HEAD')
HTTPCHK_URI = os.environ.get('HTTPCHK_URI', '/')
HTTPCHK_HOST = os.environ.get('HTTPCHK_HOST', 'localhost')

# Generate config
listen_conf = Template("""
listen stats
  bind *:$port
  stats enable
  stats uri /
  stats hide-version
  stats auth $auth
""")

frontend_conf = Template("""
frontend $name
  bind *:$port $accept_proxy
  mode $mode
  default_backend $backend
""")

if COOKIES_ENABLED:
    #if we choose to enable session stickiness
    #then insert a cookie named $COOKIES_NAME(SRV_ID) to the request:
    #all responses from HAProxy to the client will contain a Set-Cookie:
    #header with a specific value for each backend server as its cookie value.
    base_backend_conf = Template(f"""
backend $backend
  mode $mode
  balance $balance
  default-server $default_server
  cookie $cookies_name insert $cookies_params
""")
    cookies = "cookie \\\"@@value@@\\\""
else:
    # The old template and behaviour for backward compatibility
    # in this case the cookie will not be set - see below the value for
    # cookies variable (is set to empty)
    base_backend_conf = Template(f"""
backend $backend
  mode $mode
  balance $balance
  default-server $default_server
  cookie $cookies_name prefix $cookies_params
""")
    cookies = ""

backend_type_http = Template("""
  option forwardfor
  http-request set-header X-Forwarded-Port %[dst_port]
  http-request add-header X-Forwarded-Proto https if { ssl_fc }
                             
  option httpchk
  http-check connect
  http-check send meth $httpchk_method uri $httpchk_uri ver HTTP/1.1 hdr host $httpchk_host
  http-check expect status 200
""")

backend_conf_hosts = Template("""
  server $name-$index $host:$port $cookies check
""")

health_conf = """
listen healthz
  bind *:4242
"""

## Open the config file for writing
with open("/usr/local/etc/haproxy/haproxy.cfg", "w") as configuration:
    with open("/tmp/haproxy.cfg", "r") as default:
        conf = Template(default.read())
        conf = conf.substitute(
            LOGGING=LOGGING,
            LOG_LEVEL=LOG_LEVEL,
            TIMEOUT_CLIENT=TIMEOUT_CLIENT,
            TIMEOUT_CONNECT=TIMEOUT_CONNECT,
            TIMEOUT_SERVER=TIMEOUT_SERVER
        )

        configuration.write(conf)

    configuration.write(
        listen_conf.substitute(
            port=STATS_PORT, auth=STATS_AUTH
        )
    )

    ### Write Health
    configuration.write(health_conf)


    ################################################################################
    # Add the provided backends
    ################################################################################

    # Open DNS backends file
    backend_info = {}
    with open('/etc/haproxy/dns.backends', 'w') as bfile:

        for index in range(1, BACKEND_POOLS + 1):
            ips = {}
            host = os.environ.get(f"BACKEND{index}_HOST", "")
            name = os.environ.get(f"BACKEND{index}_NAME", f"backend-{host}")
            port = os.environ.get(f"BACKEND{index}_PORT", BACKEND_PORT)
            mode = os.environ.get(f"BACKEND{index}_MODE", BACKEND_MODE)
            balance = os.environ.get(f"BACKEND{index}_BALANCE", BACKEND_BALANCE)
            default_server = os.environ.get(f"BACKEND{index}_DEFAULT_SERVER", BACKEND_DEFAULT_SERVER)
            backend_info[index] = (host, name, mode)

            # Logging
            print(f"[HAProxy] Adding backend {name} with mode {mode} and bind to hostname {host}:{port}")

            # Substitute template for backend with correct values
            backend_conf = base_backend_conf.substitute(
                backend=name,
                mode=mode,
                default_server=default_server,
                balance=balance,
                cookies_name=COOKIES_NAME,
                cookies_params=COOKIES_PARAMS
            )

            # Add http check when http mode is used for this backend
            if mode == 'http':
                backend_conf += backend_type_http.substitute(
                    httpchk_method=HTTPCHK_METHOD,
                    httpchk_uri=HTTPCHK_URI,
                    httpchk_host=HTTPCHK_HOST
                )

            # Retrieve the host names
            try:
                records = subprocess.check_output(["getent", "hosts", host])
            except Exception as err:
                print(err)
            else:
                for record in records.splitlines():
                    ip = record.split()[0].decode()
                    ips[ip] = (host, port)

            # Write ips to file to keep track of changes
            bfile.write(' '.join(sorted(ips)))

            # Get base backend conf, and add hosts to it
            for ip, (host, port) in ips.items():
                backend_conf += backend_conf_hosts.substitute(
                    name=host.replace(".", "-"),
                    index=ip.replace(".", "-"),
                    host=ip,
                    port=port,
                    cookies=cookies.replace('@@value@@', ip))

            # Write current backend
            configuration.write(backend_conf)

    ################################################################################
    # Add the provided frontend
    ################################################################################

    for index in range(1, FRONTEND_POOLS + 1):
        port = os.environ.get(f"FRONTEND{index}_PORT")
        mode = os.environ.get(f"FRONTEND{index}_MODE", backend_info[index][2])
        backend = os.environ.get(f"FRONTEND{index}_BACKEND", backend_info[index][1])
        name = os.environ.get(f"FRONTEND{index}_NAME", f"frontend-{backend_info[index][0]}")

        # Logging
        print(f"[HAProxy] Adding frontend {name} with mode {mode} and bind to backend {backend} and port {port}")

        if PROXY_PROTOCOL_ENABLED:
            accept_proxy = "accept-proxy"
        else:
            accept_proxy = ""

            configuration.write(
                frontend_conf.substitute(
                    name=name,
                    port=port,
                    mode=mode,
                    backend=backend,
                    accept_proxy=accept_proxy
                )
            )