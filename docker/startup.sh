#!/bin/bash
set -e
set -x

service apache2 start
service grafana-server start
service graphios start

python /root/monitor/manage.py runserver
