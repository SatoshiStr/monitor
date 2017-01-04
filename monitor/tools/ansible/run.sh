#!/usr/bin/env bash

ansible-playbook playbook.yml -i hosts \
    -e nrpe_config=templates/nrpe.cfg \
    -e nrpe_dest=/etc/nagios/nrpe.cfg \
    -e nagios_ip=10.10.1.82 \
    -e "dec_str='gg a dec str'"
