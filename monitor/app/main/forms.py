# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, IPAddress


class HostForm(FlaskForm):
    ip = StringField(u'主机IP', validators=[IPAddress(), DataRequired()])
    hostname = StringField(u'主机名', validators=[DataRequired()])
    username = StringField(u'SSH用户名', validators=[DataRequired()])
    password = StringField(u'SSH密码')
    submit = SubmitField(u'添加')


class ServiceForm(FlaskForm):
    name = StringField(u'服务名', validators=[DataRequired()])
    submit = SubmitField(u'添加')
