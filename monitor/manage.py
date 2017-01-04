# coding=utf-8

import os
import signal

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import create_app, db
from utils.nagios import nagios_manager

def SIGTERM_handler(signum, frame):
    print '\n--- Caught SIGTERM; Attempting to quit gracefully ---'
    nagios_manager.stop()
    exit(0)

# signal.signal(signal.SIGINT , SIGTERM_handler)


if __name__ == '__main__':
    app = create_app()
    manager = Manager(app)
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
    manager.run()

