# coding=utf-8
import logging
from sqlalchemy import or_
from flask import render_template, flash, redirect, url_for, request, jsonify
from utils import nagios, ansible
from app.models import Host, Service, HostGroup
from . import main
from .forms import HostGroupForm, HostForm


@main.route('/host-group')
def host_group_list():
    form = HostGroupForm()
    groups = HostGroup.query.order_by(HostGroup.id).all()
    return render_template('host_group_list.html', groups=groups, form=form,
                           group_list_active='active')


@main.route('/host-group/<int:group_id>')
def host_group_detail(group_id):
    group = HostGroup.query.get_or_404(group_id)
    hosts = Host.query.filter_by(host_group_id=group.id).order_by(Host.id).all()
    return render_template('host_group_detail.html', group=group, hosts=hosts)


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


@main.route('/host-group/<int:group_id>/<int:host_id>/add', methods=['POST'])
def add_host_to_group(group_id, host_id):
    group = HostGroup.query.get_or_404(group_id)
    host = Host.query.get_or_404(host_id)
    group.add_host(host)
    flash(u'成功添加主机%s到主机组%s' % (host.hostname, group.name))
    return '{}'


@main.route('/host-group/<int:group_id>/<int:host_id>/remove', methods=['POST'])
def remove_host_to_group(group_id, host_id):
    group = HostGroup.query.get_or_404(group_id)
    host = Host.query.get_or_404(host_id)
    group.remove_host(host)
    flash(u'成功把主机%s移除主机组%s' % (host.hostname, group.name))
    return '{}'


@main.route('/host-group/<int:group_id>/create-host', methods=['POST'])
def create_host_at_group(group_id):
    group = HostGroup.query.get_or_404(group_id)
    form = HostForm()
    if form.validate_on_submit():
        if Host.query.filter(or_(Host.ip == form.ip.data,
                                 Host.hostname == form.hostname.data)).count():
            flash(u'添加主机失败, IP %s 或主机名 %s 已经被使用' %
                  (form.ip.data, form.hostname.data))
        else:
            host = Host.create(ip=form.ip.data, hostname=form.hostname.data,
                               username=form.username.data,
                               password=form.password.data)
            group.add_host(host)
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(url_for('main.host_group_detail'))


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
        for host in group.hosts:
            nagios.remove_service(host.hostname, service.command)
    for name in to_add:
        service = Service.query.filter_by(name=name).one()
        group.services.append(service)
        for host in group.hosts:
            nagios.add_service(host.hostname, service.name, service.command,
                               service.prefix)
    group.save()
    return '{}'
