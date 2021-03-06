#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
import csv
import io
import os

from flask import (Response, request, redirect, url_for, abort, flash,
                   render_template, current_app, make_response)
from flask.views import (View, MethodView)
from flask_babel import gettext as _
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from config import (APP_NAME, PY3, CSV_ENCODING)
from .database import db_session
from .forms import (DataEditForm, NengaForm, YearAddForm)
from .models import (Nenga, Data)

def tos(s, py3=PY3):
    if py3:
        return s
    if isinstance(s, int) or isinstance(s, float):
        return str(s)
    elif not s:
        return ''
    else:
        try:
            return s.encode('cp932', 'ignore')
        except:
            return s
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

class YearAddView(MethodView):
    def get(self):
        form = YearAddForm()
        return render_template('hagaki_sakka/year_form.html',
                               form=form,
                               title=_(u'add new year'))

    def post(self):
        form = YearAddForm(request.form)
        if form.validate():
            year = form.year.data
            object_list = db_session.query(Data).join(Nenga)\
                          .filter(Nenga.year==year)
            if object_list.count():
                form.year.errors.append(_(u'Year %(year)s is already exists',
                                        year=year))
            else:
                object_list = db_session.query(Data)\
                              .filter(Data.invalid==False)
                for obj in object_list:
                    nenga = Nenga()
                    nenga.year = year
                    nenga.data_id = obj.id
                    db_session.add(nenga)
                db_session.commit()
                return redirect(url_for('.address_list', year=year))

        return render_template('hagaki_sakka/year_form.html',
                               form=form,
                               title=_(u'add new year'))

class PersonListView(View):
    def dispatch_request(self):
        object_list = db_session.query(Data).order_by('yomi')
        return render_template('hagaki_sakka/address_list.html',
                               object_list=object_list,
                               title=_(u'all person list'))

class PersonDetailView(MethodView):
    def get(self, oid):
        data = db_session.query(Data).filter(Data.id==oid).first()
        if not data:
            abort(404)
        return render_template('hagaki_sakka/address_detail.html',
                               data=data,
                               title=_(u'detail about %(name)s',
                                       name=data.name))

class AddressListView(MethodView):
    def get(self, year):
        object_list = db_session.query(Nenga).join(Data)\
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
                current_app.logger.info(u'Add %s.' % data.name)
            except Exception as e:
                flash(_(u'Error %(error)s', error=e))
                current_app.logger.fatal(e)
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
            """
            if ((data.name, data.zipcode, data.address1, data.address2) != (form.name.data, form.zipcode.data, form.address1.data, form.address2.data)):
                update_form_data = None
                data = Data()
            else:
                update_form_data = dict(((k, v.data)
                                 for k, v in form.__dict__['_fields'].items()))
                db_session.query(Data).filter_by(id=data.id).update(update_form_data)
            """
            update_form_data = dict(((k, v.data) for k, v
                                     in form.__dict__['_fields'].items()))
            db_session.query(Data).filter_by(id=data.id)\
            .update(update_form_data)
            try:
                db_session.commit()
                if update_form_data:
                    flash(_(u'Update %(oid)s %(name)s.', oid=data.id,
                            name=data.name))
                    current_app.logger.info(u'Update %s.' % data.id)
                else:
                    old_data = Data.query.filter_by(id=oid).one()
                    old_data.invalid = True
                    flash(_(u'Add %(oid)s %(name)s.', oid=data.id,
                            name=data.name))
                    current_app.logger.info(u'Add %s.' % data.id)
                return redirect(url_for('.address_edit', oid=data.id))
            except Exception as e:
                flash(_(u'Error %(error)s', error=e))
                current_app.logger.fatal(e)
                db_session.rollback()

        return render_template('hagaki_sakka/address_form.html',
                               form=form,
                               title=_(u'edit data for %(name)s',
                                       name=data.name))

class AddressExportView(MethodView):
    def conv(self, s):
        if not s:
            s = ''
        s = s.replace(u'君', u'くん')
        s = s.replace(u'さん', u'様')
        return s

    def get(self, year=None):
        zen_space = '\u3000'
        is_netprint = True if request.args.get('netprint') else False
        if is_netprint:
            title = (u'グループ', u'姓', u'名', u'姓カナ', u'名カナ', u'敬称', u'郵便番号1', u'郵便番号2', u'都道府県', u'住所 1', u'住所 2', u'連名1名', u'連名1敬称', u'連名2名', u'連名2敬称', u'連名3名', u'連名3敬称')
            suffix = '_netprint'
        else:
            title = (u'氏名', u'ふりがな', u'敬称', u'グループ', u'郵便番号', u'住所 1', u'住所 2', u'電話番号', u'FAX番号', u'携帯電話番号', u'メール 1', u'メール 2', u'ホームページ', u'備考', u'家族 1 名前', u'家族 1 ふりがな', u'家族 1 敬称', u'家族 2 名前', u'家族 2 ふりがな', u'家族 2 敬称', u'家族 3 名前', u'家族 3 ふりがな', u'家族 3 敬称', u'家族 4 名前', u'家族 4 ふりがな', u'家族 4 敬称', u'家族 5 名前', u'家族 5 ふりがな', u'家族 5 敬称')
            suffix = ''
        data = [[tos(x) for x in title]]
        object_list = db_session.query(Data)
        if year:
            object_list = object_list.filter_by(invalid=False)\
                          .filter_by(abroad=False).join(Nenga)\
                          .filter(Nenga.year==year)\
                          .filter(Nenga.address_unknown==False)
            if not is_netprint:
                object_list = object_list.filter(Nenga.mourning==False)
        object_list = object_list.order_by(Data.yomi)
        for x in object_list:
            if is_netprint:
                fullname = x.name.split(zen_space)
                if len(fullname) == 1:
                    fullname.append(zen_space)
                lastname, firstname = fullname
                fullkana = x.yomi.split(zen_space)
                if len(fullkana) == 1:
                    fullkana.append(zen_space)
                sei, mei = fullkana
                zip1, zip2 = x.zipcode.split('-')
                group = u'年賀'
                if year:
                    for y in x.nenga:
                        if (y.year == year) and y.mourning:
                            group = u'喪中'
                row = (group, lastname, firstname, sei, mei, self.conv(x.title), zip1,
                       zip2, x.prefecture, x.address1, x.address2, x.firstname2,
                       self.conv(x.title2), x.firstname3, self.conv(x.title3),
                       x.firstname4, self.conv(x.title4))
            else:
                row = (x.name, x.yomi, x.title, '', x.zipcode, x.address1,
                       x.address2, x.tel, x.fax, x.mobile, x.mail, '', '', x.note,
                       x.firstname2, '', x.title2, x.firstname3, '', x.title3,
                       x.firstname4, '', x.title4, x.firstname5, '', x.title5)
            data.append([tos(x) for x in row])
        if PY3:
            fp = io.StringIO()
        else:
            fp = io.BytesIO()
        mime_type = 'application/octet-stream'
        writer = csv.writer(fp, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows([tos(x) for x in data])

        name = 'address' + suffix
        if year:
            name += str(year)

        output = fp.getvalue()
        if PY3:
            output = output.encode(CSV_ENCODING)

        response = make_response(output)
        response.headers['Content-Type'] = '%s' % mime_type
        response.headers['Content-Disposition'] = 'filename="%s.csv"' % name

        return response

class AddressStatusView(View):
    def dispatch_request(self):
        year = db_session.query(func.max(Nenga.year)).one()[0]
        title = (u'氏名', u'グループ', u'年', u'送信', u'受信', u'喪中', u'備考')

        data = [[tos(x) for x in title]]
        object_list = db_session.query(Data).join(Nenga).order_by(Data.yomi)

        for x in object_list:
            for y in x.nenga:
                if y.year == year:
                    send = '1' if y.send else ''
                    receive = '1' if y.receive else ''
                    mourning = '1' if y.mourning else ''
                    row = (x.name, x.note, y.year, send, receive, mourning, y.note)
                    data.append([tos(x) for x in row])
        if PY3:
            fp = io.StringIO()
        else:
            fp = io.BytesIO()
        mime_type = 'application/octet-stream'
        writer = csv.writer(fp, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows([tos(x) for x in data])

        name = 'address_status'

        output = fp.getvalue()
        if PY3:
            output = output.encode(CSV_ENCODING)

        response = make_response(output)
        response.headers['Content-Type'] = '%s' % mime_type
        response.headers['Content-Disposition'] = 'filename="%s.csv"' % name

        return response
