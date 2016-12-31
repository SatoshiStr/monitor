#!/bin/bash
set -x
set -e

: ${MYSQL_PASS:=admin123}
: ${NAGIOS_USER:=nagiosadmin}
: ${NAGIOS_PASS:=admin123}

cat << EOF | debconf-set-selections
mysql-server mysql-server/root_password password ${MYSQL_PASS}
mysql-server mysql-server/root_password_again password ${MYSQL_PASS}
mysql-server mysql-server/start_on_boot boolean true
EOF

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y apache2
apt-get install -y mysql-server mysql-client
apt-get install -y php5 php5-mysql libapache2-mod-php5
apt-get install -y nagios3 nagios-nrpe-plugin

usermod -a -G nagios www-data
chmod -R +x /var/lib/nagios3/

sed -i "s/^check_external_commands=.*/check_external_commands=1/g" /etc/nagios3/nagios.cfg

# set nagios password
htpasswd -bc /etc/nagios3/htpasswd.users ${NAGIOS_USER} ${NAGIOS_PASS}

service nagios3 restart
