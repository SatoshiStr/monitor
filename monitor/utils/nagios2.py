# coding=utf-8
"""
把数据库的配置转化为nagios配置

清空原有文件的内容，在文件写入新的配置
"""
import logging
import os
from subprocess import Popen, PIPE
import threading
import time

from config import config
from app import create_app
from app.models import Machine, Group, Service
from utils.openstack import set_env, get_all_vms

CONFIG_FILE_PREFIX = config.NAGIOS_CONFIG_FILE_PREFIX
HOST_CONFIG_FILE = config.NAGIOS_HOST_CONFIG_FILE
HOST_GROUP_CONFIG_FILE = config.NAGIOS_HOST_GROUP_CONFIG_FILE
SERVICE_CONFIG_FILE = config.NAGIOS_SERVICE_CONFIG_FILE
COMMAND_CONFIG_FILE = config.NAGIOS_COMMAND_CONFIG_FILE

LOG = logging.getLogger(__name__)



def sync():
    nagios_sync = NagiosSync()
    nagios_sync.setDaemon(True)
    nagios_sync.start()


class NagiosSync(threading.Thread):
    def __init__(self):
        super(NagiosSync, self).__init__()

    def run(self):
        # synchronize config
        # clear file
        clear_file(HOST_CONFIG_FILE)
        clear_file(HOST_GROUP_CONFIG_FILE)
        clear_file(SERVICE_CONFIG_FILE)
        #
        local_host = 'localhost'
        with create_app().app_context():
            groups = Group.query.filter_by(type='Host').all()
            for group in groups:
                host_names = [host.hostname for host in group.machines]
                members = ','.join(host_names)
                add_host_group(group.name, group.desc, members)
            for host in Machine.query.filter_by(type='Host').all():
                if host.is_monitor_host():
                    local_host = host.hostname
                prefix = 'Monitor.host'
                add_host(host.hostname, host.ip, prefix)
                if host.groups:
                    for service in host.get_services(source='group'):
                        add_service(host.hostname, service.name,
                                    service.command, prefix)
                else:
                    for service in host.services:
                        add_service(host.hostname, service.name,
                                    service.command, prefix)
            # vm
            for vm in Machine.query.filter_by(type='VM').all():
                prefix = 'Monitor.vm.' + vm.vm_id
                if vm.groups:
                    services = vm.get_services(source='group')
                    for service in services:
                        warn = service.warn if service.warn else -1
                        critic = service.critic if service.critic else -1
                        add_service(local_host, vm.vm_id[:8] + service.name,
                                    service.command % (vm.vm_id, warn, critic),
                                    prefix)
        # restart
        popen = Popen(['/etc/init.d/nagios3', 'restart'], stdout=PIPE)
        stdout = popen.stdout.read().decode('utf-8')
        ret_code = popen.wait()
        LOG.info(u'%d %s' % (ret_code, stdout))
        sync_running = False


def clear_file(file_name):
    with open(file_name, 'w') as f:
        f.write('')


config_template = u'''
define %(name)s {
    %(content)s
}
'''


def add_host_group(name, desc, members):
    config = [
        ('hostgroup_name', name),
        ('alias', desc),
    ]
    if members:
        config.append(('members', members))
    add_config('hostgroup', config, HOST_GROUP_CONFIG_FILE)


def add_host(host_name, ip, prefix='Monitor'):
    config = [
        ('use', 'generic-host'),
        ('host_name', host_name),
        ('alias', host_name),
        ('address', ip),
        ('max_check_attempts', '5'),
        ('check_period', '24x7'),
        ('notification_interval', '30'),
        ('notification_period', '24x7'),
        ('_graphiteprefix', prefix)
    ]
    add_config('host', config, HOST_CONFIG_FILE)


def add_service(host_name, service_name, check_command, prefix='Monitor'):
    config = [
        ('use', 'generic-service'),
        ('host_name', host_name),
        ('service_description', service_name),
        ('check_command', check_command),
        ('normal_check_interval', '1'),
        ('_graphiteprefix', prefix)
    ]
    add_config('service', config, SERVICE_CONFIG_FILE)


def add_config(name, config, file_name):
    content = []
    for key, value in config:
        if not isinstance(key, unicode):
            key = key.decode('utf-8')
        if not isinstance(value, unicode):
            value = value.decode('utf-8')
        temp_str = key+value
        if ' ' in temp_str or '\t' in temp_str:
            print('key or value should not contain white space.'
                     ' [%s] [%s]' % (key, value))
        content.append(u'%s   %s' % (key, value))
    result = config_template % {'name': name, 'content': u'\n    '.join(content)}
    with open(file_name, 'a') as f:
        f.write(result.encode('utf-8'))
