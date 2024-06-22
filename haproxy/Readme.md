## HAProxy Docker image with Dynamic Host-resolver

This image is generic and can be used on other projects. This version is based on the initial work provided of this image: [hub.docker.com/r/eecms/haproxy](https://hub.docker.com/r/eeacms/haproxy)

 - Debian: **Bookworm**
 - HAProxy: **3.0**
 
### Supported tags and respective Dockerfile links

  - `:latest` [*Dockerfile*](https://github.com/woutergd/docker.haproxy/blob/master/haproxy/Dockerfile) - Debian: **Bookworm**, HAProxy: **3.0**

### Stable and immutable tags

  - `:3.0` [*Dockerfile*](https://github.com/woutergd/docker.haproxy/tree/3.0/haproxy/Dockerfile) - HAProxy: **3.0** Release: **3.0**


See [all versions](https://github.com/woutergd/docker.haproxy/releases)

### Changes

 - [CHANGELOG.md](https://github.com/woutergd/docker.haproxy/blob/master/CHANGELOG.md)

### Source code

  - [github.com](http://github.com/woutergd/oss-haproxy-dns)


## Usage

### Run with Docker Compose

Here is a basic example of a `docker-compose.yml` file using the `mapgear/docker.haproxy` docker image:

    version: "2"
    services:
      haproxy:
        image: mapgear/docker.haproxy
        depends_on:
        - nginx
        ports:
        - "80:80"
        - "1936:1936"
        environment:
          FRONTEND1_PORT: 80
          BACKEND1_PORT: 5000
          BACKEND1_HOST: nginx
          LOG_LEVEL: "info"

      nginx:
        image: nginx


The application can be scaled to use more server instances, with `docker-compose scale`:

    $ docker-compose up -d --scale nginx=4

The results can be checked in a browser, navigating to http://localhost.
By refresing the page multiple times it is noticeable that the IP of the server
that served the page changes, as HAProxy switches between them.
The stats page can be accessed at http://localhost:1936 where you have to log in
using the `STATS_AUTH` authentication details (default `admin:admin`).

Note that it may take **up to one minute** until backends are plugged-in due to the
minimum possible `DNS_TTL`.

### Use a custom configuration file mounted as a volume

    $ docker run -v conf.d/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg mapgear/docker.haproxy:latest


If you edit `haproxy.cfg` you can reload it without having to restart the container:

    $ docker exec <name-of-your-container> reload


## Supported environment variables ##

As HAProxy has close to no purpose by itself, this image should be used in
combination with others (for example with [Docker Compose](https://docs.docker.com/compose/)).

HAProxy can be configured by modifying the following env variables,
either when running the container or in a `docker-compose.yml` file.

## Frontend configuration
This image allows the generation of multiple frontend pools

### Global frontend settings
  * `FRONTEND_POOLS` The number of frontend pools, default to 1
  * `FRONTEND_MODE` The mode for all the frontend pools. If not set, `BACKEND_MODE` is used as default

### Frontend pools
Per frontend pool, the following settings can be configured:
  * `FRONTEND1_NAME` The name of the frontend pool. If not set, the name of the backend pool is used
  * `FRONTEND1_PORT` The port of the frontend pool. Must be set per pool, as no default port can be deduced from config
  * `FRONTEND1_BACKEND` The name of the default backend pool for this frontend. If not set, the backend pool on the same index is used, e.g. `BACKEND3` for `FRONTEND3`


## Backend configuration
This docker image allows the generation of multiple backend pools.

#### Global Backend Settings
  * `BACKEND_POOLS` The number of backend pools. If not set, `FRONTEND_POOLS` is used so the same amount of frontend- and backend pools are created.
  * `BACKEND_PORT` The default port for all backend pools. If not set, it defaults to 5000
  * `BACKEND_MODE` The default mode for all backend pools
  * `BACKEND_BALANCE` The default balance algorithm. If not provided, defaults to `roundrobin`
  * `BACKEND_DEFAULT_SERVER` The default server options for all backend pools. Default is `inter 2s fastinter 2s downinter 2s fall 3 rise 2`. Check [https://docs.haproxy.org/2.4/configuration.html#5.2] for all the available options.

#### Backend pools
For every backend pool, a set of environment variables can be created. In the following variables, the number 1 need to be replaced per backend pool. Index starts at 1, and continues up till the number of `BACKEND_POOLS`.

The available options per pool are:
  * `BACKEND1_HOST` Host name of the servers to detect
  * `BACKEND1_NAME` Optional name of the backend in haproxy. If not set, `BACKEND1_HOST` is used as name
  * `BACKEND1_PORT` The port of the backend servers.
  * `BACKEND1_MODE` The mode of the backend servers, either `http` or `tcp`
  * `BACKEND1_DEFAULT_SERVER` Default server parameters, which are applied to all backend servers in this pool


## Other settings
  * `STATS_PORT` The port to bind statistics to - default `1936`
  * `STATS_AUTH` The authentication details (written as `user:password` for the statistics page - default `admin:admin`
  * `PROXY_PROTOCOL_ENABLED` The option to enable or disable accepting proxy protocol (`true` stands for enabled, `false` or anything else for disabled) - default `false`
  * `COOKIES_ENABLED` The option to enable or disable cookie-based sessions (`true` stands for enabled, `false` or anything else for disabled) - default `false`
  * `COOKIES_NAME` Will be added on cookie declaration - default `SRV_ID`
  * `COOKIES_PARAMS` Will be added on cookie declaration - example `indirect nocache maxidle 30m maxlife 8h` or `maxlife 24h` - documentation https://cbonte.github.io/haproxy-dconv/1.8/configuration.html#4-cookie
  * `LOGGING` Override logging ip address:port - default is udp `127.0.0.1:514` inside container
  * `LOG_LEVEL` Set haproxy log level, default is `notice` ( only send important events ). Can be: `emerg`,`alert`,`crit`,`err`,`warning`,`notice`,`info`,`debug`
  * `DNS_TTL` DNS lookup backends every `DNS_TTL` minutes. Default `1` minute.
  * `TIMEOUT_CONNECT` the maximum time to wait for a connection attempt to a VPS to succeed. Default `5000` ms
  * `TIMEOUT_CLIENT` timeouts apply when the client is expected to acknowledge or send data during the TCP process. Default `50000` ms
  * `TIMEOUT_SERVER` timeouts apply when the server is expected to acknowledge or send data during the TCP process. Default `50000` ms
  * `HTTPCHK_METHOD` The HTTP method used to check the servers health - default `HEAD`
  * `HTTPCHK_URI` The HTTP uri used to check on the servers health - default `/`
  * `HTTPCHK_HOST` Host Header override on http Health Check - default `localhost`


## Logging

By default the logs from haproxy are present in the docker log, by using the rsyslog inside the container (UDP port 514). No access logs are present by default, but this can be changed by setting the log level.

You can change the logging level by providing the `LOG_LEVEL` environment variable:

    docker run -e LOG_LEVEL=info  ... eeacms/haproxy

You can override the log output by providing the `LOGGING` environment variable:

    docker run -e LOGGING=logs.example.com:5005 ... eeacms/haproxy

Now make sure that `logs.example.com` listen on UDP port `5005`

## Copyright and license

The Initial Owner of the Original Code is European Environment Agency (EEA). Check https://github.com/eea/eea.docker.haproxy for the original version.

The modifications and code changes are provided for free by MapGear B.V. (NL) but are provided as free software.

The Original Code is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License v3 as published by the Free Software.
