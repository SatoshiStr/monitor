# coding=utf-8
import os
from subprocess import Popen, PIPE


def parse_result(text):
    text = text.strip()
    lines = text.split('\n')
    keys = parse_line(lines[1])
    results = []
    for line in lines[3:-1]:
        d = {}
        items = parse_line(line)
        for key, value in zip(keys, items):
            d[key] = value
        results.append(d)
    return results


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


def get_all_vms():
    results = run_command(
        'nova list --fields OS-EXT-SRV-ATTR:host,OS-EXT-SRV-ATTR:hostname,hostId,tenant_id')
    vms = []
    for result in results:
        vm = {
            'id': result['ID'],
            'name': result['OS-EXT-SRV-ATTR: Hostname'],
            'host': result['OS-EXT-SRV-ATTR: Host'],
            'host_id': result['hostId'],
            'tenant_id': result['Tenant Id'],
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


