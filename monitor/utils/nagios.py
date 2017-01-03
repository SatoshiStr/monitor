# coding=utf-8
from subprocess import Popen, PIPE

# CONFIG_FILE_PREFIX = './'
CONFIG_FILE_PREFIX = '/etc/nagios3/conf.d/'
HOST_CONFIG_FILE = CONFIG_FILE_PREFIX+'hosts.cfg'
SERVICE_CONFIG_FILE = CONFIG_FILE_PREFIX+'services.cfg'
COMMAND_CONFIG_FILE = CONFIG_FILE_PREFIX+'commands.cfg'


def add_host(host_name, ip):
    config = [
        ('use', 'generic-host'),
        ('host_name', host_name),
        ('alias', host_name),
        ('address', ip),
        ('max_check_attempts', '5'),
        ('check_period', '24x7'),
        ('notification_interval', '30'),
        ('notification_period', '24x7'),
        ('_graphiteprefix', 'Monitor')
    ]
    add_config('host', config, HOST_CONFIG_FILE)


def remove_host(host_name):
    remove_config(HOST_CONFIG_FILE, [('host_name', host_name)])


def add_service(host_name, service_desc, check_command, prefix):
    if not prefix:
        prefix = check_command
    config = [
        ('use', 'generic-service'),
        ('host_name', host_name),
        ('service_description', service_desc),
        ('check_command', check_command),
        ('normal_check_interval', '1'),
        ('_graphiteprefix', 'Monitor.'+prefix)
    ]
    add_config('service', config, SERVICE_CONFIG_FILE)


def remove_service(host_name, check_command):
    remove_config(SERVICE_CONFIG_FILE, [('host_name', host_name),
                                     ('check_command', check_command)])


config_template = u'''
define %(name)s {
    %(content)s
}
'''


def add_config(name, config, file_name, overwrite=False):
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
    with open(file_name, 'a' if not overwrite else 'w') as f:
        f.write(result.encode('utf-8'))
    popen = Popen(['/etc/init.d/nagios3', 'restart'])


def remove_config(file_name, criteria):
    with open(file_name) as f:
        content = f.read().decode('utf-8')
    all_configs = []
    for item in content.split('\n\n'):
        item = item.strip()
        if not item:
            continue
        lines = item.split('\n')
        name = lines[0].split()[1]
        lines = lines[1:-1]
        config = []
        for line in lines:
            k, v = line.strip().split()
            config.append((k, v))
        if not set(criteria).issubset(set(config)):
            all_configs.append((name, config))
    if all_configs:
        # rewrite to file
        overwrite = True
        for name, config in all_configs:
            add_config(name, config, file_name, overwrite=overwrite)
            if overwrite:
                overwrite = False
    else:
        # clear file
        with open(file_name, 'w') as f:
            f.write('')
    popen = Popen(['/etc/init.d/nagios3', 'restart'])


if __name__ == '__main__':
    filename = SERVICE_CONFIG_FILE
    # for i in range(4):
    #     i += 1
    #     add_config('service',
    #                [('host_name', 'host%s'%i),
    #                 ('check_command', 'check_vm'),
    #                 ('use', 'generic')],
    #                filename)
    # remove_config(filename, [('host_name', 'host1'),
    #                          ('check_command', 'check_vm2')])
    with open(filename) as f:
        print f.read()
    remove_service('mitaka', 'check_vm')
    print '============'
    with open(filename) as f:
        print f.read()
