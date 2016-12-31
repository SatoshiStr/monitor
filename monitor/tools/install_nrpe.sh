#!/bin/bash
set -x
set -e

: ${NAGIOS_IP:=10.10.1.81}

apt-get update
apt-get install -y nagios-nrpe-server nagios-plugins

sed -i "s/^allowed_hosts=.*/allowed_hosts=127.0.0.1,${NAGIOS_IP}/g"  /etc/nagios/nrpe.cfg

service nagios-nrpe-server restart
