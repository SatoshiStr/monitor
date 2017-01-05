# coding=utf-8
import logging
from sqlalchemy import or_
from flask import render_template, flash, redirect, url_for, request, jsonify
from utils import ansible
from app.models import Host, Service, HostGroup
from . import main
from .forms import HostGroupForm, MultiHostForm
from app.models import remove_exist

@main.route('/host-group')
def host_group_list():
    form = HostGroupForm()
    groups = HostGroup.query.order_by(HostGroup.id).all()
    return render_template('host_group_list.html', groups=groups, form=form,
                           group_list_active='active')


@main.route('/host-group/<int:group_id>')
def host_group_detail(group_id):
    form = MultiHostForm()
    group = HostGroup.query.get_or_404(group_id)
    group_list = HostGroup.query.order_by(HostGroup.id).all()
    hosts = Host.query.filter_by(host_group_id=group.id).order_by(Host.id).all()
    left_services = remove_exist(Service.get_all(), group.services)
    return render_template('host_group_detail.html', group=group, hosts=hosts,
                           form=form, group_list=group_list,
                           left_services=left_services,
                           selected_services=group.services)


@main.route('/host-group', methods=['POST'])
def add_group():
    form = HostGroupForm()
    if form.validate_on_submit():
        HostGroup.create(form.name.data, form.desc.data)
        flash(u'主机组%s 添加成功' % form.name.data)
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(request.args.get('next', '') or
                    url_for('main.host_group_list'))


@main.route('/host-group/<int:group_id>/remove', methods=['POST'])
def remove_group(group_id):
    group = HostGroup.query.get_or_404(group_id)
    group.delete()
    flash(u'成功删除主机组 %s' % group.name)
    return '{}'


@main.route('/host-group/<int:host_id>/move', methods=['POST'])
def move_host(host_id):
    data = request.get_json()
    to_group = HostGroup.query.filter_by(name=data.get('name')).first()
    host = Host.query.get_or_404(host_id)
    if not to_group:
        flash(u'成功把主机%s移出主机组%s' % (host.hostname, host.host_group.name))
        host.host_group.remove_host(host)
    else:
        to_group.add_host(host)
        flash(u'成功添加主机%s到主机组%s' % (host.hostname, to_group.name))
    return '{}'


@main.route('/host-group/<int:group_id>/create-hosts', methods=['POST'])
def create_hosts_at_group(group_id):
    group = HostGroup.query.get_or_404(group_id)
    form = MultiHostForm()
    if form.validate_on_submit():
        for num in range(form.ip_start.data, form.ip_end.data+1):
            ip = form.ip_prefix.data + '.' + str(num)
            hostname = form.hostname.data + '-' + str(num)
            if Host.query.filter(or_(Host.ip == ip,
                                     Host.hostname == hostname)).count():
                flash(u'添加主机失败, IP %s 或主机名 %s 已经被使用' %
                      (ip, hostname))
            else:
                host = Host.create(ip=ip, hostname=hostname,
                                   username=form.username.data,
                                   password=form.password.data)
                group.add_host(host)
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(url_for('main.host_group_detail', group_id=group_id))


@main.route('/host-group/<int:group_id>/service', methods=['POST'])
def change_group_service(group_id):
    group = HostGroup.query.get_or_404(group_id)
    all_services = Service.get_all(include_openstack=False)
    all_set = set([service.name for service in all_services])
    data = request.get_json()
    new_set = set(data).intersection(all_set)
    old_set = set([service.name for service in group.services])
    to_add = new_set - old_set
    to_delete = old_set - new_set
    for name in to_delete:
        service = Service.query.filter_by(name=name).one()
        group.services.remove(service)
    for name in to_add:
        service = Service.query.filter_by(name=name).one()
        group.services.append(service)
    group.save()
    return '{}'


@main.route('/host-group/<int:group_id>/config', methods=['POST'])
def config_host_group(group_id):
    group = HostGroup.query.get_or_404(group_id)
    task_name = ansible.deploy(group.hosts)
    for host in group.hosts:
        host.latest_task_name = task_name
        host.state = u'配置中'
        host.save()
    return '{}'


