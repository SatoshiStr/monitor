# coding=utf-8
import logging
import os

from flask import Flask, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app(config=config):
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s:%(message)s',
                        level=logging.INFO, datefmt='%m/%d/%Y %H:%M:%S')
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
