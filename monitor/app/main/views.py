# coding=utf-8
import logging
from sqlalchemy import or_
from flask import render_template, flash, redirect, url_for, request
from utils import nagios
from app.models import Host, Service
from . import main
from .forms import HostForm, ServiceForm

LOG = logging.getLogger(__name__)


@main.route('/')
def root():
    hosts = Host.get_all()
    host_form = HostForm()
    return render_template('root.html', hosts=hosts, host_form=host_form)


@main.route('/host', methods=['POST'])
def add_host():
    form = HostForm()
    if form.validate_on_submit():
        if Host.query.filter(or_(Host.ip == form.ip.data,
                                 Host.hostname == form.hostname.data)).count():
            flash(u'添加主机失败, IP %s 或主机名 %s 已经被使用' %
                  (form.ip.data, form.hostname.data))
        else:
            host = Host(ip=form.ip.data, hostname=form.hostname.data,
                        username=form.username.data, password=form.password.data)
            host.save()
            nagios.add_host(host.hostname, host.ip)
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(url_for('main.root'))


@main.route('/host/<int:host_id>/remove', methods=['POST'])
def remove_host(host_id):
    host = Host.query.get_or_404(host_id)
    for service in host.services:
        nagios.remove_service(host.hostname, service.command)
        service.delete()
    nagios.remove_host(host.hostname)
    ip = host.ip
    host.delete()
    flash(u'成功删除主机 %s' % ip)
    return '{}'


@main.route('/host/<int:host_id>/service', methods=['POST'])
def add_service(host_id):
    host = Host.query.get_or_404(host_id)
    if host.is_monitor_host():
        all_services = Service.get_all(include_openstack=True)
    else:
        all_services = Service.get_all(include_openstack=False)
    all_set = set([service.name for service in all_services])
    data = request.get_json()
    new_set = set(data).intersection(all_set)
    old_set = set([service.name for service in host.services])
    to_add = new_set - old_set
    to_delete = old_set - new_set
    for name in to_delete:
        service = Service.query.filter_by(name=name).one()
        host.services.remove(service)
        nagios.remove_service(host.hostname, service.command)
    for name in to_add:
        service = Service.query.filter_by(name=name).one()
        host.services.append(service)
        nagios.add_service(host.hostname, service.name, service.command,
                           service.prefix)
    host.save()
    return '{}'
