#!/bin/bash
set -e
set -x

/etc/init.d/mysql restart

service apache2 start
service nagios3 start

service graphios start
service grafana-server start


/etc/init.d/mysql restart

mysql -uroot -padmin123 <<EOF
create database if not exists monitor;
EOF

cd /opt/monitor
pip install -r requirements.txt
python manage.py db upgrade
python manage.py runserver --host 0.0.0.0 &
cd -


/bin/bash
