#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
import datetime
from flask import url_for
from flask.ext.babel import lazy_gettext as _
from wtforms import Form, BooleanField, IntegerField, TextField, \
     TextAreaField, SelectField
from wtforms import validators
from wtforms.validators import Length, Required, ValidationError

from config import DEFAULT_ENCODING, PERSONAL_TITLE_LIST, PY_VERSION

def title_list():
    if PY_VERSION == '3':
        result = [(x, x) for x in PERSONAL_TITLE_LIST]
        result.insert(0, ('', ''))
    else:
        result = [(unicode(x, DEFAULT_ENCODING), unicode(x, DEFAULT_ENCODING))
                  for x in PERSONAL_TITLE_LIST]
        result.insert(0, (u'', u''))

    return result

class BaseDataForm(Form):
    name = TextField(_(u'name'))
    yomi = TextField(_(u'yomi'))
    title = SelectField(_(u'personal title'),
                        validators=[Required(),],
                        choices=title_list())
    mail = TextField(_(u'mail'))
    mobile = TextField(_(u'mobile'))
    zipcode = TextField(_(u'zip code'))
    prefecture = TextField(_(u'prefecture'))
    address1 = TextField(_(u'address %(n)s', n=1))
    address2 = TextField(_(u'address %(n)s', n=2))
    tel = TextField(_(u'telephone'))
    fax = TextField(_(u'facsimile'))
    abroad = BooleanField(_(u'abroad'))
    invalid = BooleanField(_(u'invalid'))
    note = TextAreaField(_(u'note'),
                            validators=[Length(max=255)])
    firstname2 = TextField(_(u'first name %(n)s', n=2))
    title2 = SelectField(_(u'personal title %(n)s', n=2),
                        choices=title_list())
    mail2 = TextField(_(u'mail %(n)s', n=2))
    mobile2 = TextField(_(u'mobile %(n)s', n=2))
    firstname3 = TextField(_(u'first name %(n)s', n=3))
    title3 = SelectField(_(u'personal title %(n)s', n=3),
                        choices=title_list())
    mail3 = TextField(_(u'mail %(n)s', n=3))
    mobile3 = TextField(_(u'mobile %(n)s', n=3))
    firstname4 = TextField(_(u'first name %(n)s', n=4))
    title4 = SelectField(_(u'personal title %(n)s', n=4),
                        choices=title_list())
    mail4 = TextField(_(u'mail %(n)s', n=4))
    mobile4 = TextField(_(u'mobile %(n)s', n=4))
    firstname5 = TextField(_(u'first name %(n)s', n=5))
    title5 = SelectField(_(u'personal title %(n)s', n=5),
                        choices=title_list())
    mail5 = TextField(_(u'mail %(n)s', n=5))
    mobile5 = TextField(_(u'mobile %(n)s', n=5))

class DataEditForm(BaseDataForm):
    pass

class NengaForm(Form):
    send = BooleanField(_(u'send'))
    receive = BooleanField(_(u'receive'))
    mourning = BooleanField(_(u'mourning'))
    address_unknown = BooleanField(_(u'address unknown'))
    note = TextAreaField(_(u'note'), validators=[Length(max=255)])

class YearAddForm(Form):
    year = IntegerField(_(u'year'))

    def validate_year(form, field):
        try:
            int(field.data)
        except Exception as e:
            #print (e)
            raise ValidationError(_(u'Not a valid integer value'))
        year = datetime.datetime.now().year
        if (field.data < year) or (field.data > year + 10):
            raise ValidationError(_(u'Not adequate year value'))
