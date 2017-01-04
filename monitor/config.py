# coding=utf-8
import os
import re
from subprocess import Popen, PIPE

local_ips = set()
output = Popen('ifconfig', stdout=PIPE).stdout.read()
pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
match = pattern.findall(output)
for ip in match:
    if not ip.endswith('.0') and not ip.endswith('.255') and\
            not ip.endswith('.1'):
        local_ips.add(ip)


class Config:
    SECRET_KEY = '\xbe\x1b\xd6\x15\xfdp$\xb5\x8a\xeb\xd5\xa6'\
                 '\xd2\x90\xc3a6\xc9\rt\xa5\x83l\xac'
    SESSION_PROTECTION = 'basic'
    REMEMBER_COOKIE_HTTPONLY = True

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI ='mysql://root:admin123@localhost/monitor?charset=utf8'

    LOCAL_IPS = local_ips


class DevelopmentConfig(Config):
    # nagios
    NAGIOS_CONFIG_FILE_PREFIX = '/etc/nagios3/conf.d/'
    NAGIOS_HOST_CONFIG_FILE = NAGIOS_CONFIG_FILE_PREFIX + 'hosts.cfg'
    NAGIOS_HOST_GROUP_CONFIG_FILE = NAGIOS_CONFIG_FILE_PREFIX + 'hostgroups.cfg'
    NAGIOS_SERVICE_CONFIG_FILE = NAGIOS_CONFIG_FILE_PREFIX + 'services.cfg'
    NAGIOS_COMMAND_CONFIG_FILE = NAGIOS_CONFIG_FILE_PREFIX + 'commands.cfg'
    NAGIOS_IP = os.environ.get('NAGIOS_IP') or list(Config.LOCAL_IPS)[0]
    # ansible
    ANSIBLE_TASK_DIR = os.environ.get('ANSIBLE_TASK_DIR') or './ansible-tasks'
    # log
    LOG_FILE = os.environ.get('LOG_FILE', None)
    #
    DEBUG = True


config = DevelopmentConfig
