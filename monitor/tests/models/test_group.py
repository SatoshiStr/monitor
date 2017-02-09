# coding=utf-8
import pytest

from app import db
from app.models import Group, Machine, GroupMachineMap, Service, GroupService


@pytest.mark.usefixtures('rollback')
class TestGroup(object):
    def test_create(self):
        grp = Group.create_host_group('name', 'desc')
        assert grp.type == 'Host'
        assert grp.name == 'name'
        assert grp.desc == 'desc'

    def test_create2(self):
        grp = Group.create_vm_group('name', 'desc')
        assert grp.type == 'VM'
        assert grp.name == 'name'
        assert grp.desc == 'desc'

    def test_delete(self):
        m1 = Machine.create_vm('m1')
        m2 = Machine.create_vm('m2')
        grp = Group.create_vm_group('name', 'desc')
        grp2 = Group.create_vm_group('name2', 'desc')
        grp.add_machine(m1)
        grp.add_machine(m2)
        grp2.add_machine(m2)
        assert len(m2.groups) == 2
        db.session.flush()
        # delete grp1
        grp.delete()
        db.session.flush()
        assert GroupMachineMap.query.filter_by(group_id=grp.id).count() == 0
        assert Group.query.filter_by(name='name').first() is None
        assert Machine.query.filter_by(vm_id='m1').first() is None
        assert Machine.query.filter_by(vm_id='m2').first() is not None
        assert len(Machine.query.filter_by(vm_id='m2').one().groups) == 1
        # delete grp2
        grp2.delete()
        db.session.flush()
        assert Machine.query.filter_by(vm_id='m2').first() is None

    def test_add_remove_machine(self):
        m1 = Machine.create_vm('m1')
        m2 = Machine.create_vm('m2')
        grp = Group.create_vm_group('name', 'desc')
        assert len(grp.machines) == 0
        grp.add_machine(m1)
        assert len(grp.machines) == 1
        grp.add_machine(m2)
        assert len(grp.machines) == 2
        # remove
        grp.remove_machine(m1)
        assert len(grp.machines) == 1
        assert len(m1.groups) == 0
        grp.remove_machine(m2)
        assert len(grp.machines) == 0

    def test_add_remove_service(self):
        grp = Group.create_vm_group('name', 'desc')
        services = Service.get_all()
        # add
        s1 = services[0]
        grp.add_service(s1.id, 5, 6)
        assert len(grp.services) == 1
        g_s1 = GroupService.query.one()
        assert g_s1.warn == 5
        assert g_s1.critic == 6
        assert g_s1.name == s1.name
        # remove
        grp.remove_service(s1.id)
        db.session.flush()
        grp = Group.query.first()
        assert len(grp.services) == 0
        assert GroupService.query.first() is None


