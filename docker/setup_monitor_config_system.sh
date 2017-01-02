#!/bin/bash
set -e
set -x

apt-get install -y python-setuptools && easy_install pip
pip install -r /root/monitor/requirements.txt

# install ansible 1.96
apt-get install software-properties-common
apt-add-repository ppa:ansible/ansible-1.9
apt-get update
apt-get install ansible

mysql -uroot -padmin123 <<EOF
create database monitor;
EOF

python /root/monitor/manage.py migrate
