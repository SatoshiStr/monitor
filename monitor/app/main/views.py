# coding=utf-8
import logging
from sqlalchemy import or_
from flask import render_template, flash, redirect, url_for, request, jsonify
from utils import nagios2, ansible
from app.models import Machine, Service, Group
from . import main
from .forms import HostForm

LOG = logging.getLogger(__name__)


@main.route('/')
def root():
    hosts = Machine.get_all_standalone_host()
    group_list = Group.query.filter_by(type='Host').order_by(Group.id).all()
    host_form = HostForm()
    return render_template('root.html', hosts=hosts, host_form=host_form,
                           root_active='active', group_list=group_list)


@main.route('/host', methods=['POST'])
def add_host():
    form = HostForm()
    if form.validate_on_submit():
        if Machine.query. \
                filter(or_(Machine.ip == form.ip.data,
                           Machine.hostname == form.hostname.data)).count():
            flash(u'添加主机失败, IP %s 或主机名 %s 已经被使用' %
                  (form.ip.data, form.hostname.data))
        else:
            Machine.create_host(ip=form.ip.data, hostname=form.hostname.data,
                                username=form.username.data,
                                password=form.password.data)
    else:
        flash(u'表单验证失败 %s' % form.errors)
    return redirect(url_for('main.root'))


@main.route('/host/<int:host_id>/remove', methods=['POST'])
def remove_host(host_id):
    host = Machine.query.get_or_404(host_id)
    flash(u'成功删除主机 %s' % host.ip)
    if host.host_group_id:
        host.host_group.remove_host(host)
    host.delete()
    return '{}'


@main.route('/host/<int:host_id>/service', methods=['POST'])
def change_host_service(host_id):
    host = Machine.query.get_or_404(host_id)
    data = request.get_json()
    new_services = []
    for item in data:
        new_service = Service.query.filter_by(name=item['name']).first()
        if new_service:
            new_service.warn = item['warn'] or None
            new_service.critic = item['critic'] or None
            new_services.append(new_service)
    host.update_service(new_services)
    return '{}'


@main.route('/host/<int:host_id>/config', methods=['POST'])
def config_host(host_id):
    host = Machine.query.get_or_404(host_id)
    task_name = ansible.deploy((host,))
    host.latest_task_name = task_name
    host.state = u'配置中'
    host.save()
    return '{}'


@main.route('/host/<int:host_id>/config-detail', methods=['GET'])
def get_config_detail(host_id):
    host = Machine.query.get_or_404(host_id)
    with open(ansible.TASK_DIR+'/'+host.latest_task_name) as f:
        content = f.read().encode('utf-8')
    return jsonify({'stdout': content})


@main.route('/sync', methods=['POST'])
def sync():
    nagios2.sync()
    flash(u'开始同步Nagios配置')
    return '{}'
