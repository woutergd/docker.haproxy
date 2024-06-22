FROM haproxy:3.0-bookworm
LABEL maintainer="EEA: IDM2 A-Team <eea-edw-a-team-alerts@googlegroups.com>"

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    python3-pip \
    cron \
    rsyslog \
 && apt-get clean

RUN rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/local/etc/haproxy /etc/haproxy
RUN sed -i '/#cron./c\cron.*                          \/proc\/1\/fd\/1'  /etc/rsyslog.conf \
 && sed -i '/#$ModLoad imudp/c\$ModLoad imudp'  /etc/rsyslog.conf \
 && sed -i '/#$UDPServerRun/c\$UDPServerRun 514'  /etc/rsyslog.conf \
 && sed -i '/$UDPServerRun 514/a $UDPServerAddress 127.0.0.1' /etc/rsyslog.conf \
 && sed -i '/cron.*/a local2.*                          \/proc\/1\/fd\/1' /etc/rsyslog.conf

COPY src/haproxy.cfg /tmp/
COPY src/configure.py src/track_dns /

# Update entrypoint
RUN mv /usr/local/bin/docker-entrypoint.sh /usr/local/bin/haproxy-entrypoint.sh
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
