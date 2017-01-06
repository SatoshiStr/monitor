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
        clear_file(HOST_CONFIG_FILE)
        clear_file(HOST_GROUP_CONFIG_FILE)
        clear_file(SERVICE_CONFIG_FILE)
        # vm
        set_env()
        vms = get_all_vms()
        #
        with create_app().app_context():
            groups = HostGroup.query.all()
            for group in groups:
                host_names = [host.hostname for host in group.hosts]
                members = ','.join(host_names)
                add_host_group(group.name, group.desc, members)
            for host in Host.query.all():
                add_host(host.hostname, host.ip,
                         host.host_group.name if host.host_group else None)
                if host.host_group:
                    for service in host.host_group.services:
                        if service.tag == u'虚拟机':
                            # 跳过, 主机组不包含虚拟机的监控
                            continue
                        if service.prefix:
                            prefix = host.host_group.name + '.' + service.prefix
                        else:
                            prefix = host.host_group.name
                        add_service(host.hostname, service.name,
                                    service.command, prefix)
                else:
                    for service in host.services:
                        if service.prefix:
                            prefix = 'Standalone.' + service.prefix
                        else:
                            prefix = 'Standalone'
                        if service.tag == u'虚拟机':
                            prefix = service.prefix
                            for vm in vms:
                                vm_id = vm['id']
                                add_service(host.hostname, vm_id[:8] + service.name,
                                            service.command % vm_id, prefix)
                        else:
                            add_service(host.hostname, service.name,
                                        service.command, prefix)
        # restart
        popen = Popen(['/etc/init.d/nagios3', 'restart'], stdout=PIPE)
        stdout = popen.stdout.read().decode('utf-8')
        ret_code = popen.wait()
        LOG.info(u'%d %s' % (ret_code, stdout))
        sync_running = False


def parse_result(text):
    text = text.strip()
    lines = text.split('\n')
    keys = parse_line(lines[1])
    resutls = []
    for line in lines[3:-1]:
        d = {}
        items = parse_line(line)
        for key, value in zip(keys, items):
            d[key] = value
        resutls.append(d)
    return resutls


def parse_line(line):
    line = line[1:-1]
    items = line.split('|')
    for i, item in enumerate(items):
        items[i] = item.strip()
    return items


def run_command(command):
    if isinstance(command, str) or isinstance(command, unicode):
        command = command.split()
    proc = Popen(command, stdout=PIPE)
    stdout = proc.stdout.read()
    ret_code = proc.wait()
    if ret_code == 0:
        return parse_result(stdout)
    return 'fail'


def get_all_vms():
    results = run_command('nova list')
    vms = []
    for result in results:
        vm = {
            'id': result['ID'],
            'name': result['Name']
        }
        vms.append(vm)
    return vms


def set_env():
    # read env
    with open('/openrc') as f:
        for line in f:
            line = line.strip()
            if line:
                key, value = line.split()[1].split('=')
                os.environ[key] = value


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


def add_host(host_name, ip, group_name=None):
    if group_name:
        prefix = 'Monitor.' + group_name
    else:
        prefix = 'Monitor.Standalone'
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
