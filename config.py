#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
try:
    import configparser
except:
    import ConfigParser as configparser
import os
import sys

#
# setting
#
DEFAULT_ENCODING = 'utf-8'
CONFIG = configparser.ConfigParser()
try:
    CONFIG.read('default.cfg')
except:
    CONFIG.read('default.cfg', DEFAULT_ENCODING)

#
# DEFAULT section
#
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
APP_NAME = CONFIG.get('DEFAULT', 'app_name')

# admin
SECRET_KEY = CONFIG.get('admin', 'secret')

# directry
DATA_DIR = os.path.join(ROOT_DIR, 'data')
LOG_DIR = os.path.join(ROOT_DIR, 'log')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')

# database
DATABASE_PREFIX = CONFIG.get('database', 'prefix')
SQLALCHEMY_DATABASE = os.path.join(DATA_DIR, 'data.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' +  SQLALCHEMY_DATABASE
ECHO = False

# data
PERSONAL_TITLE_LIST = CONFIG.get('data', 'personal_title').split(',')

# misc
PY_VERSION = sys.version.split('.')[0]

def main(argv):
    """main function"""
    print (PERSONAL_TITLE_LIST)

if __name__ == "__main__":
    main(sys.argv)
#### config.py ends here
