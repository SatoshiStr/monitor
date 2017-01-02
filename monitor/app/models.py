# coding=utf-8
from datetime import datetime
from flask import current_app
from app import db


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


class Host(IdMixin, CreateTimeMixin, Model):
    ip = db.Column(db.String(15), nullable=False, unique=True)
    hostname = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=True, default=None)
    state = db.Column(db.Enum(u'新加入', u'配置中', u'配置完成', u'配置失败'),
                      nullable=False, default=u'新加入')
    latest_task_name = db.Column(db.String(50))

    services = db.relationship('Service', secondary='host_service_map',
                               backref=db.backref('hosts', lazy='dynamic'),
                               lazy='joined')

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
