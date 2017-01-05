#!/bin/bash

set -e
set -o pipefail

if [ -z "$LOCAL_IP" ]; then
    echo Error: LOCAL_IP is empty.
    exit 1
fi



apt-get $APT_OPTIONS -y --force-yes install ganglia-monitor
apt-get $APT_OPTIONS -y --force-yes install gmetad
# Install ganglia-webfrontend in noninteractive mode
DEBIAN_FRONTEND=noninteractive apt-get $APT_OPTIONS -y --force-yes install ganglia-webfrontend

sed -i '/^[[:space:]]*cluster[[:space:]]*{/,/}/s|name[[:space:]]*=.*|name = Monitor|g' /etc/ganglia/gmond.conf
sed -i '/^[[:space:]]*udp_send_channel[[:space:]]*{/,/}/{/mcast_join/d}' /etc/ganglia/gmond.conf
sed -i '/^[[:space:]]*udp_send_channel[[:space:]]*{/,/}/{/host/d}'  /etc/ganglia/gmond.conf
sed -i "/^[[:space:]]*udp_send_channel[[:space:]]*{/a\  host = ${LOCAL_IP}" /etc/ganglia/gmond.conf
sed -i "/^[[:space:]]*udp_recv_channel[[:space:]]*{/,/}/{s/bind[[:space:]]*=.*/bind = ${LOCAL_IP}/}" /etc/ganglia/gmond.conf

mkdir -p /etc/apache2/conf-available/
cat > /etc/apache2/conf-available/ganglia.conf <<EOF
Alias /ganglia  /usr/share/ganglia-webfrontend
<Directory "/usr/share/ganglia-webfrontend">
    Options Indexes FollowSymLinks
    AllowOverride None
    Order allow,deny
    Allow from all
</Directory>
EOF

if [ -d /etc/apache2/conf.d ]; then
    rm -rf /etc/apache2/conf.d/ganglia.conf
    ln -s /etc/apache2/conf-available/ganglia.conf  /etc/apache2/conf.d/ganglia.conf
fi
if [ -d /etc/apache2/conf-enabled ]; then
    rm -rf /etc/apache2/conf-enabled/ganglia.conf
    ln -s /etc/apache2/conf-available/ganglia.conf /etc/apache2/conf-enabled/ganglia.conf
fi

service ganglia-monitor restart
service gmetad restart
service apache2 restart
