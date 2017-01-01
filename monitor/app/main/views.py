# coding=utf-8
import logging
from flask import render_template, flash, redirect, url_for, request
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
        if Host.query.filter_by(ip=form.ip.data).count():
            flash(u'添加主机失败, IP %s 已经被使用' % form.ip.data)
        else:
            host = Host(ip=form.ip.data, hostname=form.hostname.data,
                        username=form.username.data, password=form.password.data)
            host.save()
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(url_for('main.root'))


@main.route('/host/<int:host_id>/remove', methods=['POST'])
def remove_host(host_id):
    host = Host.query.get_or_404(host_id)
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
    for name in to_add:
        service = Service.query.filter_by(name=name).one()
        host.services.append(service)
    host.save()
    return '{}'
