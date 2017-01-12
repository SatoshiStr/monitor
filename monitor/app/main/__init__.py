# coding=utf-8

from flask import Blueprint
main = Blueprint('main', __name__)

from . import views, views_host_group, views_vm_group, views_alarm
