# coding=utf-8
import pytest

from app import db
from app.models import Group, Machine, MachineService, Service


@pytest.mark.usefixtures('rollback')
class TestMachine(object):
    def test_create(self):
        grp = Machine.create_host('ip', 'hostname', 'username', 'password')
        assert grp.type == 'Host'
        assert grp.ip == 'ip'
        assert grp.hostname == 'hostname'
        assert grp.username == 'username'
        assert grp.password == 'password'

    def test_create2(self):
        grp = Machine.create_vm('vm_id')
        assert grp.type == 'VM'
        assert grp.vm_id == 'vm_id'

    def test_add_remove_service(self):
        vm = Machine.create_vm('vm_id')
        services = Service.get_all()
        # add
        s1 = services[0]
        vm.add_service(s1.id, 5, 6)
        assert len(vm.services) == 1
        g_s1 = MachineService.query.one()
        assert g_s1.warn == 5
        assert g_s1.critic == 6
        assert g_s1.name == s1.name
        # remove
        vm.remove_service(s1.id)
        db.session.flush()
        assert len(vm.services) == 0
        assert MachineService.query.first() is None

