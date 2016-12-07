#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
try:
    from ConfigParser import SafeConfigParser as ConfigParser
except:
    from configparser import ConfigParser
import io
import os
import sys

#
# setting
#
DEFAULT_ENCODING = 'utf-8'
PY3 = sys.version_info[0] == 3
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
# parser
DEFAULT_CONFIG_FILE = 'default.cfg'
SITE_CONFIG_FILE = 'site.cfg'
parser = ConfigParser()
for ini in (DEFAULT_CONFIG_FILE, ):
    fullpath = os.path.join(ROOT_DIR, ini)
    if not PY3:
        inifile = io.open(fullpath, encoding=DEFAULT_ENCODING)
        parser.readfp(inifile, fullpath)
    else:
        parser.read(fullpath)

#
# DEFAULT section
#
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
APP_NAME = parser.get('DEFAULT', 'app_name')
SITE_TITLE = parser.get('DEFAULT', 'site_title')

# admin
SECRET_KEY = parser.get('admin', 'secret')

# directry
DATA_DIR = os.path.join(ROOT_DIR, 'data')
LOG_DIR = os.path.join(ROOT_DIR, 'log')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')

# database
DATABASE_PREFIX = parser.get('database', 'prefix')
SQLALCHEMY_DATABASE = os.path.join(DATA_DIR, 'data.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' +  SQLALCHEMY_DATABASE
ECHO = False

# data
PERSONAL_TITLE_LIST = parser.get('data', 'personal_title').split(',')
DEBUG_LOG = parser.get('data', 'debug_log')
ERROR_LOG = parser.get('data', 'error_log')
CSV_ENCODING = parser.get('data', 'csv_encoding')
SENDER_LIST = parser.get('data', 'sender_list').split(',')

def main(argv):
    """main function"""
    print (PERSONAL_TITLE_LIST)

if __name__ == "__main__":
    main(sys.argv)
#### config.py ends here
