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
from app.models import Host, HostGroup, Service

CONFIG_FILE_PREFIX = config.NAGIOS_CONFIG_FILE_PREFIX
HOST_CONFIG_FILE = config.NAGIOS_HOST_CONFIG_FILE
HOST_GROUP_CONFIG_FILE = config.NAGIOS_HOST_GROUP_CONFIG_FILE
SERVICE_CONFIG_FILE = config.NAGIOS_SERVICE_CONFIG_FILE
COMMAND_CONFIG_FILE = config.NAGIOS_COMMAND_CONFIG_FILE

LOG = logging.getLogger(__name__)

sync_running = False

def sync():
    nagios_sync = NagiosSync()
    nagios_sync.setDaemon(True)
    nagios_sync.start()


class NagiosSync(threading.Thread):
    def __init__(self):
        super(NagiosSync, self).__init__()

    def run(self):
        global sync_running
        while sync_running:
            time.sleep(0.1)
        sync_running = True
        # synchronize config
        # clear file
        os.remove(HOST_CONFIG_FILE)
        os.remove(HOST_GROUP_CONFIG_FILE)
        os.remove(SERVICE_CONFIG_FILE)
        #
        with create_app().app_context():
            groups = HostGroup.query.all()
            for group in groups:
                add_host_group(group.name, group.desc)
            for host in Host.query.all():
                add_host(host.hostname, host.ip,
                         host.host_group.name if host.host_group else None)
                if host.host_group:
                    for service in host.host_group.services:
                        add_service(host.hostname, service.name,
                                    service.command, service.prefix)
                else:
                    for service in host.services:
                        add_service(host.hostname, service.name,
                                    service.command, service.prefix)
        # restart
        popen = Popen(['/etc/init.d/nagios3', 'restart'], stdout=PIPE)
        stdout = popen.stdout.read().decode('utf-8')
        ret_code = popen.wait()
        LOG.info(u'%d %s' % (ret_code, stdout))
        sync_running = False


config_template = u'''
define %(name)s {
    %(content)s
}
'''

def add_host_group(name, desc):
    config = [
        ('hostgroup_name', name),
        ('alias', desc),
        # ('_graphiteprefix', 'Monitor.hostgroup')
    ]
    add_config('hostgroup', config, HOST_GROUP_CONFIG_FILE)


def add_host(host_name, ip, group_name=None):
    config = [
        ('use', 'generic-host'),
        ('host_name', host_name),
        ('alias', host_name),
        ('address', ip),
        ('max_check_attempts', '5'),
        ('check_period', '24x7'),
        ('notification_interval', '30'),
        ('notification_period', '24x7'),
        ('_graphiteprefix', 'Monitor.host')
    ]
    if group_name:
        config.append(('hostgroup', group_name))
    add_config('host', config, HOST_CONFIG_FILE)


def add_service(host_name, service_name, check_command, prefix):
    if not prefix:
        prefix = check_command
    config = [
        ('use', 'generic-service'),
        ('host_name', host_name),
        ('service_description', service_name),
        ('check_command', check_command),
        ('normal_check_interval', '1'),
        ('_graphiteprefix', 'Monitor.'+prefix)
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
            raise ValueError('key or value should not contain white space')
        content.append(u'%s   %s' % (key, value))
    result = config_template % {'name': name, 'content': u'\n    '.join(content)}
    with open(file_name, 'a') as f:
        f.write(result.encode('utf-8'))
