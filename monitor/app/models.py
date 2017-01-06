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


class Service(IdMixin, Model):
    """
    服务分为两部分
    - 通过nagios的nrpe来获取性能信息:插件在被监控的机器上运行,因此在对应机器上配置
    - 通过openstack的sdk获取性能信息:插件在nagios安装节点运行,因此在nagios节点上配置
    """
    _physical = {
        u'CPU': [
            (u'1分钟平均负载', 'check_ganglia!load_one!4!5', ''),
            (u'5分钟平均负载', 'check_ganglia!load_five!4!5', ''),
            (u'15分钟平均负载', 'check_ganglia!load_fifteen!4!5', ''),
            (u'CPU空闲', 'check_ganglia!cpu_idle!-1!-1', ''),
        ],
        u'磁盘': [
            (u'磁盘总空间', 'check_ganglia!disk_total!-1!-1', ''),
            (u'磁盘空闲空间', 'check_ganglia!disk_free!-1!-1', ''),
        ],
        u'内存': [
            (u'内存总空间', 'check_ganglia!mem_total!-1!-1', ''),
            (u'内存空闲空间', 'check_ganglia!mem_free!-1!-1', ''),
            (u'swap总空间', 'check_ganglia!swap_total!-1!-1', ''),
            (u'swap空闲空间', 'check_ganglia!swap_free!-1!-1', ''),
        ],
        u'进程': [
            (u'进程总数', 'check_ganglia!proc_total!-1!-1', ''),
            (u'运行进程总数', 'check_ganglia!proc_run!-1!-1', ''),
        ],
        u'网络': [
            (u'每秒收到的字节数', 'check_ganglia!bytes_in!-1!-1', ''),
            (u'每秒发送的字节数', 'check_ganglia!bytes_out!-1!-1', ''),
        ],
    }
    _cloud = {
        u'虚拟机': [
            (u'虚拟机CPU使用率', 'check_vm!%s!cpu_util', 'vm'),
            (u'虚拟机内存总空间', 'check_vm!%s!memory', 'vm'),
            (u'虚拟机内存已使用空间', 'check_vm!%s!memory.usage', 'vm'),
            (u'虚拟机磁盘每秒读取字节', 'check_vm!%s!disk.read.bytes.rate', 'vm'),
            (u'虚拟机磁盘每秒写入字节', 'check_vm!%s!disk.write.bytes.rate', 'vm'),
            (u'虚拟机磁盘总空间', 'check_vm!%s!disk.capacity', 'vm'),
            (u'虚拟机磁盘已使用空间', 'check_vm!%s!disk.usage', 'vm'),
            (u'虚拟机网络每秒流入字节', 'check_vm!%s!network.incoming.bytes.rate', 'vm'),
            (u'虚拟机网络每秒流出字节', 'check_vm!%s!network.outgoing.bytes.rate', 'vm')
        ]
    }
    name = db.Column(db.String(50), nullable=False, unique=True)
    command = db.Column(db.String(50), nullable=False, unique=True)
    prefix = db.Column(db.String(50), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    type = db.Column(db.Enum('physical', 'cloud'), nullable=False)

    @staticmethod
    def init():
        for tag in Service._physical:
            for name, command, prefix in Service._physical[tag]:
                s = Service(name=name, command=command, prefix=prefix, tag=tag,
                            type='physical')
                s.save()
        for tag in Service._cloud:
            for name, command, prefix in Service._cloud[tag]:
                s = Service(name=name, command=command, prefix=prefix, tag=tag,
                            type='cloud')
                s.save()
        db.session.flush()

    @staticmethod
    def get_all(include_openstack=False):
        if Service.query.count() == 0:
            Service.init()
        if include_openstack:
            return Service.query.order_by(Service.id).all()
        else:
            return Service.query.filter_by(type='physical').order_by(
                Service.id).all()


    @staticmethod
    def to_str(services):
        return u','.join([service.name for service in services])


class HostGroup(IdMixin, CreateTimeMixin, Model):
    name = db.Column(db.String(50), nullable=False, unique=True)
    desc = db.Column(db.String(50), nullable=False, unique=True)
    host_sum = db.Column(db.Integer, default=0)

    services = db.relationship('Service', secondary='host_group_service_map',
                               backref=db.backref('groups', lazy='dynamic'),
                               lazy='joined', order_by=Service.id)
    hosts = db.relationship('Host',
                            backref=db.backref('host_group', lazy='joined'),
                            lazy='joined')

    @staticmethod
    def create(name, desc):
        group = HostGroup(name=name, desc=desc)
        group.save()

    def delete(self):
        """删除主机组和组里的所有组机
        """
        to_delete_hosts = Host.query.filter_by(host_group_id=self.id).all()
        for host in to_delete_hosts:
            host.delete()
        db.session.delete(self)

    def add_host(self, host):
        if host.host_group:
            host.host_group.host_sum -= 1
            host.host_group.save()
        self.host_sum += 1
        self.hosts.append(host)
        self.save()
        host.host_group_id = self.id
        host.save()
        assert host.host_group_id == self.id

    def remove_host(self, host):
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
                               lazy='joined',
                               order_by=Service.id)

    @staticmethod
    def create(ip, hostname, username, password):
        host = Host(ip=ip, hostname=hostname, username=username,
                    password=password)
        host.save()
        return host

    def delete(self):
        """删除主机和主机的服务
        """
        db.session.delete(self)

    def is_monitor_host(self):
        if self.ip in current_app.config['LOCAL_IPS']:
            return True
        return False

    @staticmethod
    def get_all():
        hosts = Host.query.filter_by(host_group_id=None).\
            order_by(Host.create_at).all()
        nagios_services = Service.get_all(include_openstack=True)
        other_services = Service.get_all(include_openstack=False)
        for host in hosts:
            host.selected_service_names = Service.to_str(host.services)
            if host.is_monitor_host():
                host.left_service_names = Service.\
                    to_str(remove_exist(nagios_services, host.services))
            else:
                host.left_service_names = Service.\
                    to_str(remove_exist(other_services, host.services))
        return hosts


def remove_exist(all_list, exist_list):
    for item in exist_list:
        all_list.remove(item)
    return all_list


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
