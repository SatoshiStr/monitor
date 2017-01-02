#!/bin/bash
set -e
set -x

/etc/init.d/mysql restart
service apache2 start
service nagios3 start

service graphios start
service grafana-server start

python /root/monitor/manage.py runserver

