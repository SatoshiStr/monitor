#!/bin/bash
set -x
set -e


function add_host() {
    local host_name=$1
    local ip=$2
    cat >> /etc/nagios3/conf.d/servers.cfg <<EOF

define host{
    use                     generic-host
    host_name               ${host_name}
    alias                   ${host_name}
    address                 ${ip}
    max_check_attempts      5
    check_period            24x7
    notification_interval   30
    notification_period     24x7
}

EOF
}

function add_service() {
    local host_name=$1
    local ip=$2
    cat >> /etc/nagios3/conf.d/servers.cfg <<EOF

define service {
        Use							generic-service
        host_name					${host_name}
        service_description			cpu load
        check_command			    check_load
        _graphiteprefix				Moniter.cpuload
}

EOF

}

if [ "$1" == "add-host" ]; then
    add_host $2 $3
fi
