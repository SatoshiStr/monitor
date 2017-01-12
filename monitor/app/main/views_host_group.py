# coding=utf-8
import logging
from sqlalchemy import or_
from flask import render_template, flash, redirect, url_for, request, jsonify
from utils import ansible
from app.models import Machine, Service, Group
from . import main
from .forms import HostGroupForm, MultiHostForm
from app.models import remove_exist


@main.route('/host-group')
def host_group_list():
    form = HostGroupForm()
    groups = Group.query.filter_by(type='Host').order_by(Group.id).all()
    return render_template('host_group_list.html', groups=groups, form=form,
                           group_list_active='active')


@main.route('/host-group/<int:group_id>')
def host_group_detail(group_id):
    form = MultiHostForm()
    group = Group.query.get_or_404(group_id)
    group_list = Group.query.filter_by(type='Host').order_by(Group.id).all()
    hosts = group.machines
    left_services = remove_exist(Service.get_all(), group.services)
    return render_template('host_group_detail.html', group=group, hosts=hosts,
                           form=form, group_list=group_list,
                           left_services=left_services,
                           selected_services=group.services)


@main.route('/host-group', methods=['POST'])
def add_group():
    form = HostGroupForm()
    if form.validate_on_submit():
        Group.create_host_group(form.name.data, form.desc.data)
        flash(u'主机组%s 添加成功' % form.name.data)
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(request.args.get('next', '') or
                    url_for('main.host_group_list'))


@main.route('/group/<int:group_id>/remove', methods=['POST'])
def remove_group(group_id):
    group = Group.query.get_or_404(group_id)
    if group.type == 'Host':
        flash(u'成功删除主机组 %s' % group.name)
    else:
        flash(u'成功删除虚拟机组 %s' % group.name)
    group.delete()
    return '{}'


@main.route('/host-group/<int:host_id>/move', methods=['POST'])
def change_host_group(host_id):
    data = request.get_json()
    group_names = data.get('names')
    new_groups = Group.query.filter(Group.name.in_(group_names)).all()
    host = Machine.query.get_or_404(host_id)
    for group in host.groups:
        if group not in new_groups:
            group.remove_machine(host)
            if host.type == 'Host':
                flash(u'成功把主机%s移出主机组%s' % (host.hostname, group.name))
            else:
                flash(u'成功把虚拟机%s移出虚拟机组%s' % (host.vm_id, group.name))
    for group in new_groups:
        if group not in host.groups:
            group.add_machine(host)
            if host.type == 'Host':
                flash(u'成功添加主机%s到主机组%s' % (host.hostname, group.name))
            else:
                flash(u'成功添加虚拟机%s到虚拟机组%s' % (host.hostname, group.name))
    return '{}'


@main.route('/host-group/<int:group_id>/create-hosts', methods=['POST'])
def create_hosts_at_group(group_id):
    group = Group.query.get_or_404(group_id)
    form = MultiHostForm()
    if form.validate_on_submit():
        for num in range(form.ip_start.data, form.ip_end.data+1):
            ip = form.ip_prefix.data + '.' + str(num)
            hostname = form.hostname.data + '-' + str(num)
            if Machine.query.filter(or_(Machine.ip == ip,
                                        Machine.hostname == hostname)).count():
                flash(u'添加主机失败, IP %s 或主机名 %s 已经被使用' %
                      (ip, hostname))
            else:
                host = Machine.create_host(ip=ip, hostname=hostname,
                                           username=form.username.data,
                                           password=form.password.data)
                group.add_machine(host)
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(url_for('main.host_group_detail', group_id=group_id))


@main.route('/host-group/<int:group_id>/service', methods=['POST'])
def change_group_service(group_id):
    group = Group.query.get_or_404(group_id)
    data = request.get_json()
    print data
    new_services = []
    for item in data:
        new_service = Service.query.filter_by(name=item['name']).first()
        if new_service:
            new_service.warn = item['warn'] or None
            new_service.critic = item['critic'] or None
            new_services.append(new_service)
    group.update_service(new_services)
    return '{}'


@main.route('/host-group/<int:group_id>/config', methods=['POST'])
def config_host_group(group_id):
    group = Group.query.get_or_404(group_id)
    task_name = ansible.deploy(group.machines)
    for host in group.hosts:
        host.latest_task_name = task_name
        host.state = u'配置中'
        host.save()
    return '{}'
