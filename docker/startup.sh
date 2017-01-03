#!/bin/bash
set -e
set -x

/etc/init.d/mysql restart

service apache2 start
service nagios3 start

service graphios start
service grafana-server start

cd /root/monitor/
python manage.py runserver --host 0.0.0.0 &
cd -
/bin/bash

