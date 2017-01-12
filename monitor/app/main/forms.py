# coding=utf-8
import json
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, ValidationError,\
    RadioField
from wtforms.validators import DataRequired, IPAddress, NumberRange, Email
from app.models import MailServer


class HostForm(FlaskForm):
    ip = StringField(u'主机IP', validators=[IPAddress(), DataRequired()])
    hostname = StringField(u'主机名', validators=[DataRequired()])
    username = StringField(u'SSH用户名', validators=[DataRequired()])
    password = StringField(u'SSH密码')
    submit = SubmitField(u'添加')


class ServiceForm(FlaskForm):
    name = StringField(u'服务名', validators=[DataRequired()])
    submit = SubmitField(u'添加')


class HostGroupForm(FlaskForm):
    name = StringField(u'主机组名', validators=[DataRequired()])
    desc = StringField(u'主机组描述', validators=[DataRequired()])
    submit = SubmitField(u'添加')


class MultiHostForm(FlaskForm):
    ip_prefix = StringField(u'IP前缀', validators=[DataRequired()])
    ip_start = IntegerField(u'开始IP',
                            validators=[DataRequired(),
                                        NumberRange(min=1, max=255)])
    ip_end = IntegerField(u'结束IP',
                          validators=[DataRequired(),
                                      NumberRange(min=1, max=255)])
    hostname = StringField(u'主机名前缀', validators=[DataRequired()])
    username = StringField(u'SSH用户名', validators=[DataRequired()])
    password = StringField(u'SSH密码')
    submit = SubmitField(u'添加')

    def validate_ip_prefix(form, field):
        if field.data.endswith('.'):
            field.data = field.data[:-1]
        nums = field.data.split('.')
        if len(nums) != 3:
            raise ValidationError(u'IP前缀 格式错误')
        for num in nums:
            try:
                num = int(num)
            except:
                raise ValidationError(u'IP前缀 格式错误')
            if num < 1 or num > 255:
                raise ValidationError(u'IP前缀 格式错误')


class MailForm(FlaskForm):
    mail = StringField(u'邮箱地址', validators=[DataRequired(), Email()])
    desc = StringField(u'描述', validators=[DataRequired()])
    submit = SubmitField(u'添加')


class MailServerForm(FlaskForm):
    server = StringField('', validators=[DataRequired()])
    port = IntegerField('', validators=[DataRequired()])
    use_ssl = RadioField('', choices=[('use', u'使用ssl'), ('not', u'不使用ssl')])
    username = StringField('', validators=[DataRequired()])
    password = StringField('', validators=[DataRequired()])

    def __init__(self, init=True):
        if init:
            super(MailServerForm, self).__init__()
            mail_server = MailServer.query.first()
            if not mail_server:
                mail_config = {}
            else:
                mail_config = json.loads(mail_server.data)
            print mail_config
            self.server.data=mail_config.get('MAIL_SERVER',
                                             'smtp.163.com')
            self.use_ssl.data = mail_config.get('MAIL_USE_SSL', 'use')
            self.port.data=mail_config.get('MAIL_PORT', 465)
            self.username.data=mail_config.get('MAIL_USERNAME', '')
            self.password.data=mail_config.get('MAIL_PASSWORD', '')
        else:
            super(MailServerForm, self).__init__()
