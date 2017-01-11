# coding=utf-8
import os
from subprocess import Popen, PIPE

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
    # results = run_command('nova list')
    results = [
        {
            'ID': '1',
            'Name': 'ins1',
            'Host': 'compute1'
        },
        {
            'ID': '2',
            'Name': 'ins2',
            'Host': 'compute1'
        },
        {
            'ID': '3',
            'Name': 'ins3',
            'Host': 'control'
        }
    ]
    vms = []
    for result in results:
        vm = {
            'id': result['ID'],
            'name': result['Name'],
            'host': result['Host']
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


