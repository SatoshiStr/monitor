# coding=utf-8
from datetime import datetime
import logging
import os
import threading
from subprocess import Popen, PIPE

from config import config

NAGIOS_IP = config.NAGIOS_IP
TASK_DIR = config.ANSIBLE_TASK_DIR

LOG = logging.getLogger(__name__)


class AnsibleTask(threading.Thread):
    def __init__(self, name, host_ids, inventory, args):
        super(AnsibleTask, self).__init__()
        self.task_name = name
        self.host_ids = host_ids
        self.inventory = inventory
        self.command = ['ansible-playbook', 'tools/ansible/playbook.yml',
                        '-i', self.inventory] + args

    def run(self):
        print self.command
        popen = Popen(self.command, stdout=PIPE)
        stdout = popen.stdout.read()
        ret_code = popen.wait()
        LOG.info('Ansible Task %s has a result' % stdout)
        # write output
        with open('%s/%s' % (TASK_DIR, self.task_name), 'w') as f:
            f.write(stdout)
        # remove inventory file
        os.remove(self.inventory)
        # save result to db
        from app import create_app
        from app.models import Host
        with create_app().app_context():
            for host_id in self.host_ids:
                host = Host.query.get(host_id)
                if ret_code == 0:
                    host.state = u'配置完成'
                else:
                    host.state = u'配置失败'
                host.save()


def make_inventory(hosts):
    host_text = '[monitor_target]\n'
    for host in hosts:
        template = ('%(ip)s '
                    'ansible_ssh_user=%(ssh_user)s '
                    'ansible_ssh_pass=%(ssh_pass)s '
                    'ansible_become_pass=%(ssh_pass)s\n')
        line = template % {
            'ip': host.ip,
            'ssh_user': host.username,
            'ssh_pass': host.password or ''
        }
        host_text += line
    return host_text


def deploy(hosts):
    task_name = datetime.now().strftime('%m%d:%H:%M:%S') + hosts[0].hostname
    inventory_file = 'tools/ansible/host-%s' % task_name
    with open(inventory_file, 'w') as f:
        f.write(make_inventory(hosts))
    host_ids = [host.id for host in hosts]
    task = AnsibleTask(task_name, host_ids, inventory_file,
                       ['-e', 'nrpe_config=templates/nrpe.cfg',
                        '-e', 'nrpe_dest=/etc/nagios/nrpe.cfg',
                        '-e', 'nagios_ip='+NAGIOS_IP])
    task.start()
    return task_name
