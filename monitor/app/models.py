# coding=utf-8
from datetime import datetime
from flask import current_app
from sqlalchemy.ext.declarative import declared_attr
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


class Group(IdMixin, Model):
    type = db.Column(db.Enum('Host', 'VM'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(50), nullable=False)

    machines = db.relationship('Machine',
                               secondary='group_machine_map',
                               backref=db.backref('groups', lazy='joined'),
                               lazy='joined', order_by='Machine.id')
    services = db.relationship('GroupService', lazy='joined')

    @staticmethod
    def create_host_group(name, desc):
        group = Group(type='Host', name=name, desc=desc)
        group.save()
        return group

    @staticmethod
    def create_vm_group(name, desc):
        group = Group(type='VM', name=name, desc=desc)
        group.save()
        return group

    def delete(self):
        """删除主机组和组里的所有组机（如果主机只在该组里）
        """
        to_deletes = []
        for machine in self.machines:
            if len(machine.groups) == 1 and machine.groups[0].id == self.id:
                to_deletes.append(machine)
        for machine in to_deletes:
            machine.delete()
        db.session.delete(self)

    def add_machine(self, machine):
        self.machines.append(machine)
        self.save()

    def remove_machine(self, machine):
        self.machines.remove(machine)
        self.save()

    def add_service(self, service_id, warn=None, critic=None):
        service = GroupService(service_id=service_id, warn=warn, critic=critic)
        service.save()
        self.services.append(service)
        self.save()

    def remove_service(self, service_id):
        service = GroupService.query.\
            filter_by(group_id=self.id, service_id=service_id).first()
        service.delete()


class Machine(IdMixin, Model):
    type = db.Column(db.Enum('Host', 'VM'), nullable=False)
    use_self_service = db.Column(db.Boolean, default=False)

    # host
    ip = db.Column(db.String(15), unique=True)
    hostname = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    state = db.Column(db.Enum(u'新加入', u'配置中', u'配置完成', u'配置失败'),
                      nullable=False, default=u'新加入')
    latest_task_name = db.Column(db.String(50))
    # vm
    vm_id = db.Column(db.String(50))

    services = db.relationship('MachineService', lazy='joined')

    @staticmethod
    def create_host(ip, hostname, username, password):
        host = Machine(type='Host', ip=ip, hostname=hostname, username=username,
                       password=password)
        host.save()
        return host

    @staticmethod
    def create_vm(vm_id):
        vm = Machine(type='VM', vm_id=vm_id)
        vm.save()
        return vm

    def delete(self):
        """删除主机和主机的服务
        """
        db.session.delete(self)

    def is_monitor_host(self):
        if self.ip in current_app.config['LOCAL_IPS']:
            return True
        return False

    @staticmethod
    def get_all_standalone_host():
        """返回所有不在主机组内的主机
        """
        hosts = Machine.query.outerjoin(GroupMachineMap).\
            filter(GroupMachineMap.group_id == None). \
            order_by(Machine.id).all()
        nagios_services = Service.get_all(include_openstack=True)
        other_services = Service.get_all(include_openstack=False)
        for host in hosts:
            selected = []
            for service in host.services:
                selected.append('%s-%s-%s' % (service.name, service.warn,
                                              service.critic))
            host.selected_service_names = ','.join(selected)
            if host.is_monitor_host():
                host.left_service_names = Service. \
                    to_str(remove_exist(nagios_services, host.services))
            else:
                host.left_service_names = Service. \
                    to_str(remove_exist(other_services, host.services))
        return hosts

    def add_service(self, service_id, warn=None, critic=None):
        service = MachineService(service_id=service_id, warn=warn,
                                 critic=critic)
        service.save()
        self.services.append(service)
        self.save()

    def remove_service(self, service_id):
        service = MachineService.query. \
            filter_by(machine_id=self.id, service_id=service_id).first()
        service.delete()


def update_service(self, services):
    new_service_dict = dict([(s.id, s) for s in services])
    new_id_set = set([s.id for s in services])
    old_id_set = set([s.service_id for s in self.services])
    for s_id in old_id_set - new_id_set:
        self.remove_service(s_id)
    for s_id in new_id_set - old_id_set:
        self.add_service(s_id, new_service_dict[s_id].warn,
                         new_service_dict[s_id].critic)
    common_set = new_id_set.intersection(old_id_set)
    for service in self.services:
        if service.service_id in common_set:
            service.warn = new_service_dict[service.service_id].warn
            service.critic = new_service_dict[service.service_id].critic
            service.save()


Group.update_service = update_service
Machine.update_service = update_service



class GroupMachineMap(Model):
    __tablename__ = 'group_machine_map'
    group_id = db.Column(db.Integer, db.ForeignKey(Group.id), primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey(Machine.id),
                           primary_key=True)


class Service(IdMixin, Model):
    """
    服务分为两部分
    - 通过nagios的nrpe来获取性能信息:插件在被监控的机器上运行,因此在对应机器上配置
    - 通过openstack的sdk获取性能信息:插件在nagios安装节点运行,因此在nagios节点上配置
    """
    _physical = {
        u'CPU': [
            (u'1分钟平均负载', 'check_ganglia!load_one!%s!%s', ''),
            (u'5分钟平均负载', 'check_ganglia!load_five!%s!%s', ''),
            (u'15分钟平均负载', 'check_ganglia!load_fifteen!%s!%s', ''),
            (u'CPU空闲', 'check_ganglia!cpu_idle!%s!%s', ''),
        ],
        u'磁盘': [
            (u'磁盘总空间', 'check_ganglia!disk_total!%s!%s', ''),
            (u'磁盘空闲空间', 'check_ganglia!disk_free!%s!%s', ''),
        ],
        u'内存': [
            (u'内存总空间', 'check_ganglia!mem_total!%s!%s', ''),
            (u'内存空闲空间', 'check_ganglia!mem_free!%s!%s', ''),
            (u'swap总空间', 'check_ganglia!swap_total!%s!%s', ''),
            (u'swap空闲空间', 'check_ganglia!swap_free!%s!%s', ''),
        ],
        u'进程': [
            (u'进程总数', 'check_ganglia!proc_total!%s!%s', ''),
            (u'运行进程总数', 'check_ganglia!proc_run!%s!%s', ''),
        ],
        u'网络': [
            (u'每秒收到的字节数', 'check_ganglia!bytes_in!%s!%s', ''),
            (u'每秒发送的字节数', 'check_ganglia!bytes_out!%s!%s', ''),
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
        include_openstack = False
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


def remove_exist(all_list, exist_list):
    inner_list = [item.service for item in exist_list]
    for item in inner_list:
        if item in all_list:
            all_list.remove(item)
    return all_list


class ServiceMap(Model):
    __abstract__ = True

    @declared_attr
    def service_id(self):
        return db.Column(db.Integer, db.ForeignKey(Service.id),
                         primary_key=True)
    warn = db.Column(db.Integer, default=None)
    critic = db.Column(db.Integer, default=None)

    @declared_attr
    def service(self):
        return db.relationship(Service, lazy='joined')

    @property
    def name(self):
        return self.service.name

    @property
    def command(self):
        if self.service.type == 'physical':
            warn = self.warn if self.warn is not None else -1
            critic = self.critic if self.critic is not None else -1
            return self.service.command % (warn, critic)
        elif self.service.type == 'cloud':
            return self.service.command

    @property
    def prefix(self):
        return self.service.prefix


class MachineService(ServiceMap):
    __tablename__ = 'machine_service'
    machine_id = db.Column(db.Integer, db.ForeignKey(Machine.id),
                           primary_key=True)


class GroupService(ServiceMap):
    __tablename__ = 'group_service'
    group_id = db.Column(db.Integer, db.ForeignKey(Group.id), primary_key=True)

