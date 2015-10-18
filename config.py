#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
try:
    import configparser
except:
    import ConfigParser as configparser
import os
import sys

#
# version
#
PY_VERSION = sys.version.split('.')[0]
if PY_VERSION == '3':
    PY3 = True
else:
    PY3 = False

#
# setting
#
DEFAULT_ENCODING = 'utf-8'
CONFIG = configparser.ConfigParser()

if PY3:
    CONFIG.read('default.cfg', DEFAULT_ENCODING)
else:
    CONFIG.read('default.cfg')

# function
def u2(s):
    if not PY3:
        return unicode(s, DEFAULT_ENCODING)
    return s

#
# DEFAULT section
#
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
APP_NAME = CONFIG.get('DEFAULT', 'app_name')
SITE_TITLE = u2(CONFIG.get('DEFAULT', 'site_title'))

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
DEBUG_LOG = CONFIG.get('data', 'debug_log')
ERROR_LOG = CONFIG.get('data', 'error_log')

def main(argv):
    """main function"""
    print (PERSONAL_TITLE_LIST)

if __name__ == "__main__":
    main(sys.argv)
#### config.py ends here
