#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask, Response, request, url_for, render_template, abort, \
     make_response, session, redirect, flash
try:
    from flask_babel import Babel
    from flask_babel import gettext as _
except:
    from flaskext.babel import Babel
    from flaskext.babel import gettext as _

from config import APP_NAME
from database import db_session
from forms import DataEditForm, NengaForm
from models import Nenga, Data

##
## application set up
##
app = Flask(__name__)
app.config.from_pyfile('config.py')

# error handler
#http://flask.pocoo.org/docs/patterns/errorpages/
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

##
## logging
##

# formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# file handler (common)
hdlr = RotatingFileHandler(os.path.join(app.config.get('LOG_DIR'),'%info.log'))
hdlr.setFormatter(formatter)
app.logger.addHandler(hdlr)

##
## views
##
@app.route('/')
def index():
    object_list = [x[0] for x in db_session.query(Nenga.year)\
                   .group_by(Nenga.year).order_by(Nenga.year.desc()).all()]
    return render_template('index.html',
                           object_list=object_list,
                           title=_(u'top page'))

@app.route('/user/', strict_slashes=True)
def user_list():
    object_list = db_session.query(Data).order_by('yomi')
    return render_template('address_list.html',
                           object_list=object_list,
                           title=_(u'all user list'))

@app.route('/<int:year>/', strict_slashes=True)
def address_list(year):
    object_list = db_session.query(Data).join(Nenga)\
                  .filter(Nenga.year==year).order_by('yomi')
    return render_template('address_list.html',
                           year=year,
                           object_list=object_list,
                           title=_(u'address list (%(year)s)', year=year))

@app.route('/<int:year>/<int:oid>/', methods=['GET', 'POST'],
           strict_slashes=True)
def address_detail(year, oid):
    # get nenga
    nenga = db_session.query(Nenga).join(Data).filter(Nenga.year==year)\
            .filter(Data.id==oid).first()
    if not nenga:
        raise abort(404)

    # form
    if request.method == 'GET':
        form = NengaForm(send=nenga.send, receive=nenga.receive,
                         note=nenga.note)
    else:
        form = NengaForm(request.form)
        if form.validate():
            nenga.send = form.send.data
            nenga.receive = form.receive.data
            nenga.note = form.note.data
            try:
                db_session.commit()
                app.logger.info(u'Update %s %s.' % (year, oid))
                flash(_(u'Update %(year)s %(oid)s.', year=year, oid=oid))
            except Exception as e:
                flash(_(u'Error %(error)s', error=e))
                app.logger.fatal(e)
                db_session.rollback()
                
            return redirect(url_for('.address_detail', year=year, oid=oid))

    # get data list
    object_list = db_session.query(Data).join(Nenga)\
                  .filter(Nenga.year==year).order_by('yomi')
    ids = [x.id for x in object_list]
    current_index = ids.index(oid)
    data = object_list[current_index]

    # navigation
    _prev = None
    _next = None
    try:
        if current_index:
            _prev = ids[current_index-1]
    except:
        pass
    try:
        _next = ids[current_index+1]
    except:
        pass
    
    return render_template('address_detail.html',
                           year=year,
                           obj=data,
                           form=form,
                           prev=object_list.filter(Data.id==_prev).first(),
                           next=object_list.filter(Data.id==_next).first(),
                           title=_(u'detail data for %(name)s',
                                   name=data.name))

@app.route('/<int:oid>/edit/', methods=['GET', 'POST'],
           strict_slashes=True)
def address_edit(oid):
    try:
        data = Data.query.filter_by(id=oid).one()
    except:
        abort(404)
    if request.method == 'GET':
        form = DataEditForm(**data.__dict__)
    else:
        form = DataEditForm(request.form)
        if form.validate():
            if ((data.name, data.zipcode, data.address1, data.address2) != (form.name.data, form.zipcode.data, form.address1.data, form.address2.data)):
                update_form_data = None
                data = Data()
            else:
                update_form_data = dict(((k, v.data)
                                 for k, v in form.__dict__['_fields'].items()))
                db_session.query(Data).filter_by(id=data.id).update(update_form_data)
            try:
                db_session.commit()
                if update_form_data:
                    flash(_(u'Update %(oid)s %(name)s.', oid=data.id,
                            name=data.name))
                    app.logger.info(u'Update %s.' % data.id)
                else:
                    old_data = Data.query.filter_by(id=oid).one()
                    old_data.invalid = True
                    flash(_(u'Add %(oid)s %(name)s.', oid=data.id,
                            name=data.name))
                    app.logger.info(u'Add %s.' % data.id)
                return redirect(url_for('.address_edit', oid=data.id))
            except Exception as e:
                flash(_(u'Error %(error)s', error=e))
                app.logger.fatal(e)
                db_session.rollback()
            
    return render_template('address_form.html',
                           form=form,
                           title=_(u'edit data for %(name)s',
                                   name=data.name))

@app.route('/add/', methods=['GET', 'POST'], strict_slashes=True)
def address_add():
    if request.method == 'GET':        
        form = DataEditForm()
    else:
        form = DataEditForm(request.form)
        if form.validate():
            data = Data()
            for k, v in form.__dict__['_fields'].items():
                data.__dict__[k] = v.data
            db_session.add(data)
            try:
                db_session.commit()
                flash(_(u'Add %(oid)s %(name)s.', oid=data.id, name=data.name))
                app.logger.info(u'Add %s.' % data.name)
            except Exception as e:
                flash(_(u'Error %(error)s', error=e))
                app.logger.fatal(e)
                db_session.rollback()

    return render_template('address_form.html',
                           form=form,
                           title=_(u'add new address'))

@app.route('/export/<int:year>/', strict_slashes=True)
def address_export(year):
    return 'Use comand line<br />$ pyhon3 main.py -y %s -m export' % year

##
## main
##
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
