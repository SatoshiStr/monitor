#!/bin/bash
set -x
set -e

: ${GRAPHITE_USER:=nagiosadmin}
: ${GRAPHITE_PASS:=admin123}

apt-get update
apt-get install -y apache2 libapache2-mod-wsgi python-django python-twisted \
    python-cairo python-pip python-django-tagging
pip install pytz whisper carbon graphite-web

cp /opt/graphite/conf/carbon.conf.example /opt/graphite/conf/carbon.conf
cp /opt/graphite/conf/storage-schemas.conf.example /opt/graphite/conf/storage-schemas.conf
cp /opt/graphite/conf/graphite.wsgi.example /opt/graphite/conf/graphite.wsgi


cat > /etc/apache2/sites-available/graphite-vhost.conf <<EOF
Listen 8008
<IfModule !wsgi_module.c>
    LoadModule wsgi_module modules/mod_wsgi.so
</IfModule>
WSGISocketPrefix /var/run/apache2/wsgi
<VirtualHost *:8008>
        ServerName graphite
        DocumentRoot "/opt/graphite/webapp"
        ErrorLog /opt/graphite/storage/log/webapp/error.log
        CustomLog /opt/graphite/storage/log/webapp/access.log common
        WSGIDaemonProcess graphite processes=5 threads=5 display-name='%{GROUP}' inactivity-timeout=120
        WSGIProcessGroup graphite
        WSGIApplicationGroup %{GLOBAL}
        WSGIImportScript /opt/graphite/conf/graphite.wsgi process-group=graphite application-group=%{GLOBAL}
        WSGIScriptAlias / /opt/graphite/conf/graphite.wsgi
        Alias /content/ /opt/graphite/webapp/content/
        <Location "/content/">
                SetHandler None
        </Location>
        Alias /media/ "@DJANGO_ROOT@/contrib/admin/media/"
        <Location "/media/">
                SetHandler None
        </Location>
        <Directory /opt/graphite/conf/>
                Order deny,allow
                Allow from all
        </Directory>
</VirtualHost>
EOF

ln -s /etc/apache2/sites-available/graphite-vhost.conf /etc/apache2/sites-enabled/graphite-vhost.conf

sed -i "/^<Directory \/>/,/^<\/Directory>/c<Directory \/>\n        Options FollowSymLinks\n        AllowOverride None\n        # Require all denied\n<\/Directory>" /etc/apache2/apache2.conf


apt-get install -y expect
cat >exp1 <<EOF
#!/usr/bin/expect
spawn python /opt/graphite/webapp/graphite/manage.py syncdb
expect "*(yes/no):"
send "no\n"
interact
EOF
expect exp1
cat >exp2 <<EOF
#!/usr/bin/expect
spawn python /opt/graphite/webapp/graphite/manage.py createsuperuser --username=${GRAPHITE_USER} --email=admin@admin.com
expect "Password:"
send "${GRAPHITE_PASS}\n"
expect "Password (again):"
send "${GRAPHITE_PASS}\n"
interact
EOF
expect exp2
chown -R www-data:www-data /opt/graphite/storage/
cp /opt/graphite/webapp/graphite/local_settings.py.example /opt/graphite/webapp/graphite/local_settings.py
/etc/init.d/apache2 restart

/opt/graphite/bin/carbon-cache.py start

# install graphios
apt-get install -y git
git clone https://github.com/shawn-sterling/graphios.git
cd graphios
python setup.py install
mkdir -p /var/spool/nagios/graphios
chown nagios:nagios -R /var/spool/nagios
cd -

cat > /etc/nagios3/conf.d/graphios_commands.cfg <<EOF
define command {
    command_name    graphite_perf_host
    command_line    /bin/mv  /var/spool/nagios/graphios/host-perfdata /var/spool/nagios/graphios/host-perfdata.\$TIMET$
}
define command {
    command_name    graphite_perf_service
    command_line    /bin/mv /var/spool/nagios/graphios/service-perfdata /var/spool/nagios/graphios/service-perfdata.\$TIMET$
}
EOF


sed -i "s/^enable_carbon.*=.*/enable_carbon = True/g" /etc/graphios/graphios.cfg
sed -i "s/^config_file = ''/config_file = '\/etc\/graphios\/graphios.cfg'/g" /usr/local/bin/graphios.py

mkdir -p /usr/local/nagios/var
touch /usr/local/nagios/var/graphios.log
chmod a+x /usr/local/nagios/var/graphios.log

sed -i "s/^process_performance_data=.*/process_performance_data=1/g" /etc/nagios3/nagios.cfg
cat >>/etc/nagios3/nagios.cfg <<EOF
service_perfdata_file=/var/spool/nagios/graphios/service-perfdata
service_perfdata_file_template=DATATYPE::SERVICEPERFDATA\tTIMET::\$TIMET$\tHOSTNAME::\$HOSTNAME$\tSERVICEDESC::\$SERVICEDESC$\tSERVICEPERFDATA::\$SERVICEPERFDATA$\tSERVICECHECKCOMMAND::\$SERVICECHECKCOMMAND$\tHOSTSTATE::\$HOSTSTATE$\tHOSTSTATETYPE::\$HOSTSTATETYPE$\tSERVICESTATE::\$SERVICESTATE$\tSERVICESTATETYPE::\$SERVICESTATETYPE$\tGRAPHITEPREFIX::\$_SERVICEGRAPHITEPREFIX$\tGRAPHITEPOSTFIX::\$_SERVICEGRAPHITEPOSTFIX$

service_perfdata_file_mode=a
service_perfdata_file_processing_interval=15
service_perfdata_file_processing_command=graphite_perf_service

host_perfdata_file=/var/spool/nagios/graphios/host-perfdata
host_perfdata_file_template=DATATYPE::HOSTPERFDATA\tTIMET::\$TIMET$\tHOSTNAME::\$HOSTNAME$\tHOSTPERFDATA::\$HOSTPERFDATA$\tHOSTCHECKCOMMAND::\$HOSTCHECKCOMMAND$\tHOSTSTATE::\$HOSTSTATE$\tHOSTSTATETYPE::\$HOSTSTATETYPE$\tGRAPHITEPREFIX::\$_HOSTGRAPHITEPREFIX$\tGRAPHITEPOSTFIX::\$_HOSTGRAPHITEPOSTFIX$

host_perfdata_file_mode=a
host_perfdata_file_processing_interval=15
host_perfdata_file_processing_command=graphite_perf_host
EOF

service graphios start
service nagios3 restart
