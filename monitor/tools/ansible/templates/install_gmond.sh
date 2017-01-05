#!/bin/bash

set -e

: ${CONTROL_MNG_IP:="10.10.1.110"}
: ${HOST_MNG_IP:="10.10.1.82"}

apt-get $APT_OPTIONS -y --force-yes install ganglia-monitor

sed -i '/^[[:space:]]*cluster[[:space:]]*{/,/}/s|name[[:space:]]*=.*|name = Monitor|g' /etc/ganglia/gmond.conf
sed -i '/^[[:space:]]*udp_send_channel[[:space:]]*{/,/}/{/mcast_join/d}' /etc/ganglia/gmond.conf
sed -i '/^[[:space:]]*udp_send_channel[[:space:]]*{/,/}/{/host/d}'  /etc/ganglia/gmond.conf
sed -i "/^[[:space:]]*udp_send_channel[[:space:]]*{/a\  host = ${CONTROL_MNG_IP}" /etc/ganglia/gmond.conf
sed -i "/^[[:space:]]*udp_recv_channel[[:space:]]*{/,/}/{s/bind[[:space:]]*=.*/bind = $HOST_MNG_IP/}" /etc/ganglia/gmond.conf

service ganglia-monitor restart
