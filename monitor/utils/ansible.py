# coding=utf-8
from datetime import datetime
import threading
from subprocess import Popen, PIPE

TASK_DIR = './ansible-tasks'


class AnsibleTask(threading.Thread):
    def __init__(self, name, host_id):
        super(AnsibleTask, self).__init__()
        self.task_name = name
        self.host_id = host_id

    def run(self):
        popen = Popen('tools/ansible/run.sh', stdout=PIPE)
        print 'started======'
        stdout = popen.stdout.read()
        ret_code = popen.wait()
        print 'resulted===='
        with open('%s/%s' % (TASK_DIR, self.task_name), 'w') as f:
            f.write(stdout)
        from app import create_app
        from app.models import Host
        with create_app().app_context():
            host = Host.query.get(self.host_id)
            if ret_code == 0:
                host.state = u'配置完成'
            else:
                host.state = u'配置失败'
            host.save()
        return stdout, ret_code

    @staticmethod
    def create(host):
        template = (u'[monitor_target]\n'
                    u'%(ip)s ansible_ssh_user=%(ssh_user)s '
                    u'ansible_ssh_pass=%(ssh_pass)s '
                    u'ansible_become_pass=%(ssh_pass)s\n')
        with open('tools/ansible/hosts', 'w') as f:
            content = template % {
                'ip': host.ip,
                'ssh_user': host.username,
                'ssh_pass': host.password or u''
            }
            f.write(content.decode('utf-8'))
        task_name = datetime.now().strftime('%m%d:%H:%M:%S') + host.hostname
        task = AnsibleTask(task_name, host.id)
        task.start()
        return task_name


if __name__ == '__main__':
    print AnsibleTask.create('mitaka')
