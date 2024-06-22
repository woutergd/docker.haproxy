#!/bin/bash

# Backends are resolved using internal or external DNS service
touch /etc/haproxy/dns.backends
python3 /configure.py dns

# Add crontab for DNS resolver
echo "*/${DNS_TTL:-1} * * * * /track_dns  | logger " > /var/crontab.txt
crontab /var/crontab.txt
chmod 600 /etc/crontab

# Add env variables for haproxy
echo "export PATH=$PATH"':$PATH' >> /etc/environment

# Global frontend parameters
if [ -n "$FRONTEND_POOLS" ]; then echo "export FRONTEND_POOLS=\"$FRONTEND_POOLS\""  >> /etc/environment; fi

# Get parameters per frontend pool
for i in $(seq 0 $FRONTEND_POOLS);
do
    # Get index (starting from 1)
    idx=$(( $i + 1 ))

    # Set variables per frontend
    frontend_name_var="FRONTEND${idx}_NAME"
    frontend_port_var="FRONTEND${idx}_PORT"
    frontend_backend_var="FRONTEND${idx}_BACKEND"
    frontend_mode_var="FRONTEND${idx}_MODE"
    if [ -n "${!frontend_name_var}" ]; then echo "export ${frontend_name_var}=\"${!frontend_name_var}\""  >> /etc/environment; fi
    if [ -n "${!frontend_port_var}" ]; then echo "export ${frontend_port_var}=\"${!frontend_port_var}\""  >> /etc/environment; fi
    if [ -n "${!frontend_backend_var}" ]; then echo "export ${frontend_backend_var}=\"${!frontend_backend_var}\""  >> /etc/environment; fi
    if [ -n "${!frontend_mode_var}" ]; then echo "export ${frontend_mode_var}=\"${!frontend_mode_var}\""  >> /etc/environment; fi
done

# Global backend parameters
if [ -n "$BACKEND_POOLS" ]; then echo "export BACKEND_POOLS=\"$BACKEND_POOLS\""  >> /etc/environment; fi
if [ -n "$BACKEND_PORT" ]; then echo "export BACKEND_PORT=\"$BACKEND_PORT\""  >> /etc/environment; fi
if [ -n "$BACKEND_BALANCE" ]; then echo "export BACKEND_BALANCE=\"$BACKEND_BALANCE\""  >> /etc/environment; fi
if [ -n "$BACKEND_MODE" ]; then echo "export BACKEND_MODE=\"$BACKEND_MODE\""  >> /etc/environment; fi
if [ -n "$BACKEND_DEFAULT_SERVER" ]; then echo "export BACKEND_DEFAULT_SERVER=\"$BACKEND_DEFAULT_SERVER\""  >> /etc/environment; fi

# Get parameters per backend pool
for i in $(seq 0 $BACKEND_POOLS);
do
    # Get index (starting from 1)
    idx=$(( $i + 1 ))

    # Set variables per backend
    backend_name_var="BACKEND${idx}_NAME"
    backend_host_var="BACKEND${idx}_HOST"
    backend_port_var="BACKEND${idx}_PORT"
    backend_mode_var="BACKEND${idx}_MODE"
    backend_balance_var="BACKEND${idx}_BALANCE"
    backend_default_server_var="BACKEND${idx}_DEFAULT_SERVER"
    if [ -n "${!backend_name_var}" ]; then echo "export ${backend_name_var}=\"${!backend_name_var}\""  >> /etc/environment; fi
    if [ -n "${!backend_host_var}" ]; then echo "export ${backend_host_var}=\"${!backend_host_var}\""  >> /etc/environment; fi
    if [ -n "${!backend_port_var}" ]; then echo "export ${backend_port_var}=\"${!backend_port_var}\""  >> /etc/environment; fi
    if [ -n "${!backend_mode_var}" ]; then echo "export ${backend_mode_var}=\"${!backend_mode_var}\""  >> /etc/environment; fi
    if [ -n "${!backend_balance_var}" ]; then echo "export ${backend_balance_var}=\"${!backend_balance_var}\""  >> /etc/environment; fi
    if [ -n "${!backend_default_server_var}" ]; then echo "export ${backend_default_server_var}=\"${!backend_default_server_var}\""  >> /etc/environment; fi
done

if [ -n "$COOKIES_ENABLED" ]; then echo "export COOKIES_ENABLED=\"$COOKIES_ENABLED\""  >> /etc/environment; fi
if [ -n "$COOKIES_NAME" ]; then echo "export COOKIES_NAME=\"$COOKIES_NAME\""  >> /etc/environment; fi
if [ -n "$COOKIES_PARAMS" ]; then echo "export COOKIES_PARAMS=\"$COOKIES_PARAMS\""  >> /etc/environment; fi
if [ -n "$FRONTEND_NAME" ]; then echo "export FRONTEND_NAME=\"$FRONTEND_NAME\""  >> /etc/environment; fi
if [ -n "$FRONTEND_PORT" ]; then echo "export FRONTEND_PORT=\"$FRONTEND_PORT\""  >> /etc/environment; fi
if [ -n "$FRONTEND_MODE" ]; then echo "export FRONTEND_MODE=\"$FRONTEND_MODE\""  >> /etc/environment; fi
if [ -n "$HTTPCHK" ]; then echo "export HTTPCHK=\"$HTTPCHK\""  >> /etc/environment; fi
if [ -n "$HTTPCHK_HOST" ]; then echo "export HTTPCHK_HOST=\"$HTTPCHK_HOST\""  >> /etc/environment; fi
if [ -n "$LOGGING" ]; then echo "export LOGGING=\"$LOGGING\""  >> /etc/environment; fi
if [ -n "$LOG_LEVEL" ]; then echo "export LOG_LEVEL=\"$LOG_LEVEL\""  >> /etc/environment; fi
if [ -n "$PROXY_PROTOCOL_ENABLED" ]; then echo "export PROXY_PROTOCOL_ENABLED=\"$PROXY_PROTOCOL_ENABLED\""  >> /etc/environment; fi
if [ -n "$STATS_AUTH" ]; then echo "export STATS_AUTH=\"$STATS_AUTH\""  >> /etc/environment; fi
if [ -n "$STATS_PORT" ]; then echo "export STATS_PORT=\"$STATS_PORT\""  >> /etc/environment; fi
if [ -n "$TIMEOUT_CLIENT" ]; then echo "export TIMEOUT_CLIENT=\"$TIMEOUT_CLIENT\""  >> /etc/environment; fi
if [ -n "$TIMEOUT_CONNECT" ]; then echo "export TIMEOUT_CONNECT=\"$TIMEOUT_CONNECT\""  >> /etc/environment; fi
if [ -n "$TIMEOUT_SERVER" ]; then echo "export TIMEOUT_SERVER=\"$TIMEOUT_SERVER\""  >> /etc/environment; fi

# Start logging
# TODO: With Debian Bookworm, rsyslog doesn't seem to work anymore
#service rsyslog restart

# Start crontab
service cron restart

exec /usr/local/bin/haproxy-entrypoint.sh "$@"
