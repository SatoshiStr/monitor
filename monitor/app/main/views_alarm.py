# coding=utf-8
import json
from sqlalchemy import or_
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_mail import Mail as f_mail, Message
from app.models import Machine, Service, Group, Alarm, Mail, MailServer
from . import main
from .forms import HostGroupForm, MultiHostForm, MailForm, MailServerForm


@main.route('/alarm')
def alarm_list():
    page = request.args.get('page', 1, type=int)
    pagination = Alarm.query.order_by(Alarm.id.desc()).paginate(page, 20)
    return render_template('alarm.html', pagination=pagination,
                           alarm_active='active')


@main.route('/alarm/add', methods=['POST'])
def add_alarm():
    data = request.get_json()
    data['content'] = data['content'].replace('\\n', '\n')
    alarm = Alarm(**data)
    alarm.save()
    try:
        recipients = Mail.query.all()
        recipients = [r.mail for r in recipients]
        server = MailServer.query.first()
        mail_config = json.loads(server.data)
        current_app.config.update(**mail_config)
        mail = f_mail(current_app)
        msg = Message(subject=data['subject'],
                      sender=current_app.config.get('MAIL_USERNAME', ''),
                      recipients=recipients)
        msg.html = data['content']
        mail.send(msg)
    except Exception as e:
        print e
    return '{}'


@main.route('/alarm/mail')
def show_mail():
    mail_form = MailForm()
    server_form = MailServerForm()
    mails = Mail.query.all()
    return render_template('mail.html', mail_form=mail_form,
                           server_form=server_form, mails=mails,
                           mail_list_active='active')


@main.route('/alarm/mail/add', methods=['POST'])
def add_mail():
    mail_form = MailForm()
    if mail_form.validate_on_submit():
        mail = Mail(mail=mail_form.mail.data, desc=mail_form.desc.data)
        mail.save()
        flash(u'添加邮件成功')
    else:
        flash(u'表单验证失败')
    return redirect(url_for('main.show_mail'))


@main.route('/alarm/mail/<int:mail_id>/remove', methods=['POST'])
def remove_mail(mail_id):
    mail = Mail.query.get_or_404(mail_id)
    flash(u'成功删除邮件%s' % mail.mail)
    mail.delete()
    return '{}'


@main.route('/alarm/mail-server', methods=['POST', 'GET'])
def change_mail_server():
    form = MailServerForm(init=False)
    if form.validate_on_submit():
        server = MailServer.query.first()
        if not server:
            server = MailServer(data=json.dumps({}))
            server.save()
        mail_config = dict(MAIL_SERVER=form.server.data,
                           MAIL_PORT=form.port.data,
                           MAIL_USE_SSL=form.use_ssl.data,
                           MAIL_USERNAME=form.username.data,
                           MAIL_PASSWORD=form.password.data)
        current_app.config.update(**mail_config)
        server.data = json.dumps(mail_config)
        server.save()

        flash(u'修改邮件服务器配置成功')
    else:
        flash(u'表单验证失败%s' % form.errors)
    return redirect(url_for('main.show_mail'))
