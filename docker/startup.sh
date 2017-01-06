#!/bin/bash
set -e
set -x
source /root/openrc

/etc/init.d/mysql restart

service ganglia-monitor restart
service gmetad restart
service apache2 start
service nagios3 start

/opt/graphite/bin/carbon-cache.py start
service graphios start
service grafana-server start


mysql -uroot -padmin123 <<EOF
create database if not exists monitor;
EOF

cd /opt/monitor
source /opt/monitor/env.sh
pip install -r /opt/monitor/requirements.txt
python manage.py db upgrade
python manage.py runserver --host 0.0.0.0 &
cd -

/bin/bash
