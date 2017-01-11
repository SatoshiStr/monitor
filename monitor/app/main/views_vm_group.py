# coding=utf-8
from sqlalchemy import or_
from flask import render_template, flash, redirect, url_for, request, jsonify
from utils import ansible, openstack
from app.models import Machine, Service, Group
from . import main
from .forms import HostGroupForm, MultiHostForm
from app.models import remove_exist


@main.route('/vm-group')
def vm_group_list():
    form = HostGroupForm()
    groups = Group.query.filter_by(type='VM').order_by(Group.id).all()
    return render_template('vm_group_list.html', groups=groups, form=form,
                           vm_list_active='active')


@main.route('/vm-group', methods=['POST'])
def add_vm_group():
    form = HostGroupForm()
    if form.validate_on_submit():
        Group.create_vm_group(form.name.data, form.desc.data)
        flash(u'虚拟机组%s 添加成功' % form.name.data)
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(request.args.get('next', '') or
                    url_for('main.vm_group_list'))


@main.route('/vm-group/<int:group_id>')
def vm_group_detail(group_id):
    group = Group.query.get_or_404(group_id)
    group_list = Group.query.filter_by(type='VM').order_by(Group.id).all()
    vms = group.machines
    left_services = remove_exist(Service.get_all(), group.services)
    return render_template('vm_group_detail.html', group=group, hosts=vms,
                           group_list=group_list,
                           left_services=left_services,
                           selected_services=group.services)


@main.route('/vm-group/refresh-vm')
def refresh_vm():
    openstack.set_env()
    vms = openstack.get_all_vms()
    vm_dict = dict([(vm['id'], vm) for vm in vms])
    grp_dict = {}
    for vm in vms:
        if vm['host'] not in grp_dict:
            grp_dict[vm['host']] = []
        grp_dict[vm['host']].append(vm)
    for grp in grp_dict:
        q_grp = Group.query.filter_by(type='VM', name=grp).first()
        if q_grp:
            # delete the extra vm in q_grp
            print q_grp.name
            for vm in q_grp.machines:
                print vm.vm_id
                if vm.vm_id not in vm_dict:
                    q_grp.remove_machine(vm)
        else:
            q_grp = Group.create_vm_group(grp, '宿主机 '+grp)
        for vm in grp_dict[grp]:
            vm_ins = Machine.query.filter_by(vm_id=vm['id']).first()
            if not vm_ins:
                vm_ins = Machine.create_vm(vm['id'])
            if vm_ins not in q_grp.machines:
                q_grp.add_machine(vm_ins)
    return redirect(url_for('main.vm_group_list'))
