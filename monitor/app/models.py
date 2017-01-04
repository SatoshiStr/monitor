# coding=utf-8
from datetime import datetime
from flask import current_app
from app import db
from utils import nagios


class Model(db.Model):
    __abstract__ = True

    def save(self):
        db.session.add(self)

    def delete(self):
        db.session.delete(self)


class IdMixin(object):
    id = db.Column(db.Integer, primary_key=True)


class CreateTimeMixin(object):
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)


class HostGroup(IdMixin, CreateTimeMixin, Model):
    name = db.Column(db.String(50), nullable=False, unique=True)
    desc = db.Column(db.String(50), nullable=False, unique=True)
    host_sum = db.Column(db.Integer, default=0)

    services = db.relationship('Service', secondary='host_group_service_map',
                               backref=db.backref('groups', lazy='dynamic'),
                               lazy='joined')
    hosts = db.relationship('Host',
                            backref=db.backref('host_group', lazy='joined'),
                            lazy='joined')

    @staticmethod
    def create(name, desc):
        group = HostGroup(name=name, desc=desc)
        group.save()
        nagios.add_host_group(name, desc)

    def delete(self):
        """删除主机组和组里的所有组机，同时清理nagios配置
        """
        to_delete_hosts = Host.query.filter_by(host_group_id=self.id).all()
        for host in to_delete_hosts:
            host.delete()
        nagios.remove_host_group(self.name)
        db.session.delete(self)

    def add_host(self, host):
        """清除主机的所有服务，并替换为主机组的服务"""
        for service in host.services:
            nagios.remove_service(host.hostname, service.command)
        if host.host_group_id:
            for service in host.host_group.services:
                nagios.remove_service(host.hostname, service.command)
        for service in self.services:
            nagios.add_service(host.hostname, service.name, service.command,
                               service.prefix)
        #
        if host.host_group:
            host.host_group.host_sum -= 1
            host.host_group.save()
        self.host_sum += 1
        self.hosts.append(host)
        self.save()
        print host.host_group_id, '======='
        assert host.host_group_id == self.id
        nagios.remove_host(host.hostname)
        nagios.add_host(host.hostname, host.ip, host.host_group.name)

    def remove_host(self, host):
        for service in host.host_group.services:
            nagios.remove_service(host.hostname, service.command)
        for service in host.services:
            nagios.add_service(host.hostname, service.name, service.command,
                               service.prefix)
        self.host_sum -= 1
        self.hosts.remove(host)
        self.save()


class Host(IdMixin, CreateTimeMixin, Model):
    ip = db.Column(db.String(15), nullable=False, unique=True)
    hostname = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=True, default=None)
    state = db.Column(db.Enum(u'新加入', u'配置中', u'配置完成', u'配置失败'),
                      nullable=False, default=u'新加入')
    latest_task_name = db.Column(db.String(50))
    host_group_id = db.Column(db.Integer, db.ForeignKey(HostGroup.id))

    services = db.relationship('Service', secondary='host_service_map',
                               backref=db.backref('hosts', lazy='dynamic'),
                               lazy='joined')

    @staticmethod
    def create(ip, hostname, username, password):
        host = Host(ip=ip, hostname=hostname, username=username,
                    password=password)
        host.save()
        nagios.add_host(hostname, ip)

    def delete(self):
        """删除主机和主机的服务，同时清理nagios配置
        """
        # clear service config
        for service in self.services:
            nagios.remove_service(self.hostname, service.command)
        # clear host config
        nagios.remove_host(self.hostname)
        # delete db record
        db.session.delete(self)

    def is_monitor_host(self):
        if self.ip in current_app.config['LOCAL_IPS']:
            return True
        return False

    @staticmethod
    def get_all():
        hosts = Host.query.order_by(Host.create_at).all()
        nagios_services = Service.get_all(include_openstack=True)
        other_services = Service.get_all(include_openstack=False)
        for host in hosts:
            host.selected_service_names = Service.to_str(host.services)
            if host.is_monitor_host():
                host.left_service_names = Service.\
                    to_str(set(nagios_services)-set(host.services))
            else:
                host.left_service_names = Service.\
                    to_str(set(other_services)-set(host.services))
        return hosts


class Service(IdMixin, Model):
    """
    服务分为两部分
    - 通过nagios的nrpe来获取性能信息:插件在被监控的机器上运行,因此在对应机器上配置
    - 通过openstack的sdk获取性能信息:插件在nagios安装节点运行,因此在nagios节点上配置
    """
    openstack_service_range = {u'虚拟机内存', u'虚拟机CPU使用率'}
    service_range = {u'内存', u'CPU负载', u'网卡使用率'}
    service_range.update(openstack_service_range)

    commands = {
        u'虚拟机内存': ('check_vm_mem', 'vm.cpu'),
        u'虚拟机CPU使用率': ('check_vm_cpu', 'vm.memory'),
        u'内存': ('check_mem', 'physical.memory'),
        u'CPU负载': ('check_cpu', 'physical.cpu'),
        u'网卡使用率': ('check_if', 'physical.interface')
    }

    name = db.Column(db.String(50), nullable=False, unique=True)

    @property
    def command(self):
        return Service.commands[self.name][0]

    @property
    def prefix(self):
        return Service.commands[self.name][1]

    @staticmethod
    def get_all(include_openstack=False):
        services = Service.query.all()
        exist_set = set([service.name for service in services])
        to_add = Service.service_range - exist_set
        for name in to_add:
            service = Service(name=name)
            service.save()
        if to_add:
            services = Service.query.all()
        results = []
        if not include_openstack:
            for service in services:
                if service.name not in Service.openstack_service_range:
                    results.append(service)
        else:
            results = services
        return results

    @staticmethod
    def to_str(services):
        return u','.join([service.name for service in services])


class HostServiceMap(Model):
    __tablename__ = 'host_service_map'
    host_id = db.Column(db.Integer, db.ForeignKey(Host.id), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey(Service.id),
                           primary_key=True)


class HostGroupServiceMap(Model):
    __tablename__ = 'host_group_service_map'
    group_id = db.Column(db.Integer, db.ForeignKey(HostGroup.id),
                         primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey(Service.id),
                           primary_key=True)
