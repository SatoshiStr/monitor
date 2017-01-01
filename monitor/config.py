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
    DEBUG = True


config = DevelopmentConfig
