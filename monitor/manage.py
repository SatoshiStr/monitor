# coding=utf-8

import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import create_app, db

if __name__ == '__main__':
    #

    #
    app = create_app()
    manager = Manager(app)
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
    manager.run()

