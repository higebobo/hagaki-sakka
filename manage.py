#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
from flask.ext.script import Manager, Server

from app import app_factory

manager = Manager(app_factory)
#manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('runserver', Server(use_debugger=True, use_reloader=True,
                                        host='0.0.0.0'))

if __name__ == '__main__':
    manager.run()
