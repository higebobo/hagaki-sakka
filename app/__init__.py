#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
import logging
from logging.handlers import (RotatingFileHandler, SMTPHandler)
import os

from flask import (Flask, request, redirect, session, url_for, flash,
                   render_template)
from flask.ext.babel import Babel
from flask.ext.babel import gettext as _

from .views import (IndexView, YearListView, YearAddView, PersonListView,
                    PersonDetailView, AddressListView, AddressDetailView,
                    AddressAddView, AddressEditView, AddressExportView,
                    AddressStatusView)

def not_exist_makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def app_factory(config='config', name=__name__, max_byte=100000,
                backup_count=10):
    app = Flask(name)
    app.config.from_object(config)
    # logging
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    )
    ## debug log
    debug_log = os.path.join(app.config['LOG_DIR'], app.config['DEBUG_LOG'])
    not_exist_makedirs(os.path.dirname(debug_log))
    debug_file_handler = RotatingFileHandler(debug_log, maxBytes=max_byte,
                                             backupCount=backup_count)
    debug_file_handler.setLevel(logging.INFO)
    debug_file_handler.setFormatter(formatter)
    app.logger.addHandler(debug_file_handler)
    ## error log (file handler)
    error_log = os.path.join(app.config['LOG_DIR'], app.config['ERROR_LOG'])
    not_exist_makedirs(os.path.dirname(error_log))
    error_file_handler = RotatingFileHandler(error_log, maxBytes=max_byte,
                                             backupCount=backup_count)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)
    # set default level
    app.logger.setLevel(logging.DEBUG)
    
    # routing
    app.add_url_rule('/', view_func=IndexView.as_view('index'))
    app.add_url_rule('/year/', view_func=YearListView.as_view('year_list'))
    app.add_url_rule('/year/<int:year>/', strict_slashes=True,
                     view_func=AddressListView.as_view('address_list'))
    address_detail_view_func = AddressDetailView.as_view('address_detail')
    app.add_url_rule('/year/<int:year>/<int:oid>/', methods=['GET', 'POST'],
                     strict_slashes=True,
                     view_func=address_detail_view_func)
    app.add_url_rule('/year/add/', strict_slashes=True,
                     view_func=YearAddView.as_view('year_add'))
    app.add_url_rule('/add/', methods=['GET', 'POST'], strict_slashes=True,
                     view_func=AddressAddView.as_view('address_add'))
    app.add_url_rule('/edit/<int:oid>/', methods=['GET', 'POST'],
                     strict_slashes=True,
                     view_func=AddressEditView.as_view('address_edit'))
    app.add_url_rule('/list/', strict_slashes=True,
                     view_func=PersonListView.as_view('person_list'))
    app.add_url_rule('/list/<int:oid>/', strict_slashes=True,
                     view_func=PersonDetailView.as_view('person_detail'))
    export_view_func = AddressExportView.as_view('address_export')
    app.add_url_rule('/export/', strict_slashes=True,
                     view_func=export_view_func)
    app.add_url_rule('/export/<int:year>/', strict_slashes=True,
                     view_func=export_view_func)
    app.add_url_rule('/status/', strict_slashes=True,
                     view_func=AddressStatusView.as_view('address_status'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    
    # babel
    babel = Babel(app)
    @babel.localeselector    
    def get_locale():
        return request.accept_languages.best_match(['ja', 'ja_JP', 'en'])

    return app
