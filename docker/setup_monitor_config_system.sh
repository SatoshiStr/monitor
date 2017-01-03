#!/bin/bash
set -e
set -x

pip install -r /root/monitor/requirements.txt

# install ansible 1.96
apt-get install -y software-properties-common
apt-add-repository ppa:ansible/ansible-1.9
apt-get update
apt-get install -y ansible

# suspend check
mkdir -p /root/.ssh
cat << EOF | sudo tee "/root/.ssh/config"
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
EOF

## change mysql charset
apt-get install -y crudini
crudini --set /etc/mysql/conf.d/a.cnf mysqld character-set-server utf8
/etc/init.d/mysql restart

mysql -uroot -padmin123 <<EOF
create database monitor;
EOF

cd /root/monitor/
python manage.py db upgrade

