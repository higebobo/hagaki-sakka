#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
try:
    from cStringIO import StringIO
except:
    from io import StringIO
import csv
import os

from flask import Response, request, redirect, url_for, abort, flash, \
     render_template, current_app, make_response
from flask.views import View, MethodView
from flask.ext.babel import gettext as _
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from config import APP_NAME
from .database import db_session
from .forms import DataEditForm, NengaForm
from .models import Nenga, Data

def tos(s):
    if not s:
        return ''
    try:
        return s.encode('cp932', 'ignore')
    except:
        return s

class IndexView(View):
    def dispatch_request(self):
        year = db_session.query(func.max(Nenga.year)).one()[0]
        return redirect(url_for('.address_list', year=year))

class YearListView(View):        
    def dispatch_request(self):
        object_list = [x[0] for x in db_session.query(Nenga.year)\
                       .group_by(Nenga.year).order_by(Nenga.year.desc()).all()]
        return render_template('hagaki_sakka/year_list.html',
                               object_list=object_list,
                               title=_(u'year list'))

class PersonListView(View):
    def dispatch_request(self):
        object_list = db_session.query(Data).order_by('yomi')
        return render_template('hagaki_sakka/address_list.html',
                               object_list=object_list,
                               title=_(u'all person list'))

class AddressListView(MethodView):
    def get(self, year):
        object_list = db_session.query(Data).join(Nenga)\
                      .filter(Nenga.year==year).order_by('yomi')
        return render_template('hagaki_sakka/address_list.html',
                               year=year,
                               object_list=object_list,
                               title=_(u'address list (%(year)s)', year=year))

class AddressDetailView(MethodView):
    def is_exist(self, oid, year=None):
        try:
            nenga = db_session.query(Nenga).join(Data).filter(Data.id==oid)\
                    .order_by(Nenga.year.desc())
            if year:
                nenga = nenga.filter(Nenga.year==year).one()
            return nenga
        except NoResultFound:
            abort(404)

    def get(self, oid, year):
        nenga = self.is_exist(oid, year)
        form = NengaForm(send=nenga.send, receive=nenga.receive,
                         mourning=nenga.mourning,
                         address_unknown=nenga.address_unknown,
                         note=nenga.note)

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
        
        return render_template('hagaki_sakka/address_detail.html',
                               year=year,
                               obj=data,
                               form=form,
                               prev=object_list.filter(Data.id==_prev).first(),
                               next=object_list.filter(Data.id==_next).first(),
                               history=self.is_exist(oid),
                               title=_(u'detail data for %(name)s (%(year)s)',
                                       name=data.name, year=year))

    def post(self, oid, year):
        nenga = self.is_exist(oid, year)
        form = NengaForm(request.form)
        if form.validate():
            nenga.send = form.send.data
            nenga.receive = form.receive.data
            nenga.mourning = form.mourning.data
            nenga.address_unknown = form.address_unknown.data
            nenga.note = form.note.data
            try:
                db_session.commit()
                current_app.logger.info(u'Update %s %s.' % (year, oid))
                flash(_(u'Update %(year)s %(oid)s.', year=year, oid=oid))
            except Exception as e:
                flash(_(u'Error %(error)s', error=e))
                current_app.logger.fatal(e)
                db_session.rollback()
                
            return redirect(url_for('.address_detail', year=year, oid=oid))

class AddressAddView(MethodView):
    def get(self):
        form = DataEditForm()
        return render_template('hagaki_sakka/address_form.html',
                               form=form,
                               title=_(u'add new address'))
    def post(self):
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

        return render_template('hagaki_sakka/address_form.html',
                               form=form,
                               title=_(u'add new address'))

class AddressEditView(MethodView):
    def is_exist(self, oid):
        try:
            data = Data.query.filter_by(id=oid).one()
            return data
        except:
            abort(404)

    def get(self, oid):
        data = self.is_exist(oid)
        form = DataEditForm(**data.__dict__)
        return render_template('hagaki_sakka/address_form.html',
                               form=form,
                               title=_(u'edit data for %(name)s',
                                       name=data.name))

    def post(self, oid):
        data = self.is_exist(oid)
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
            
        return render_template('hagaki_sakka/address_form.html',
                               form=form,
                               title=_(u'edit data for %(name)s',
                                       name=data.name))

class AddressExportView(MethodView):
    def get(self, year):
        title = (u'氏名', u'ふりがな', u'敬称', u'グループ', u'郵便番号', u'住所 1', u'住所 2', u'電話番号', u'FAX番号', u'携帯電話番号', u'メール 1', u'メール 2', u'ホームページ', u'備考', u'家族 1 名前', u'家族 1 ふりがな', u'家族 1 敬称', u'家族 2 名前', u'家族 2 ふりがな', u'家族 2 敬称', u'家族 3 名前', u'家族 3 ふりがな', u'家族 3 敬称', u'家族 4 名前', u'家族 4 ふりがな', u'家族 4 敬称', u'家族 5 名前', u'家族 5 ふりがな', u'家族 5 敬称')
    
        data = [[tos(x) for x in title]]
        for x in db_session.query(Data).filter_by(invalid=False)\
                .filter_by(abroad=False).join(Nenga).filter(Nenga.year==year):
            row = (x.name, x.yomi, x.title, '', x.zipcode, x.address1,
                   x.address2, x.tel, x.fax, x.mobile, x.mail, '', '', x.note,
                   x.firstname2, '', x.title2, x.firstname3, '', x.title3,
                   x.firstname4, '', x.title4, x.firstname5, '', x.title5)
            data.append([tos(x) for x in row])

        fp = StringIO()
        mime_type = 'application/octet-stream'
        writer = csv.writer(fp, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)
        response = make_response(fp.getvalue())
        response.headers['Content-Type'] = '%s' % mime_type
        response.headers['Content-Disposition'] = 'filename="address.csv"'
        
        return response
