#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
import csv
import codecs
import os
from optparse import OptionParser

from sqlalchemy.sql import func

from config import SQLALCHEMY_DATABASE, DATA_DIR, PERSONAL_TITLE_LIST
from database import create_db, db_session
from models import Data, Nenga

def import_data_from_csv(year, init=False, truncate=False):
    if init:
        if os.path.exists(SQLALCHEMY_DATABASE):
            os.unlink(SQLALCHEMY_DATABASE)
        create_db()

    if truncate:
        Nenga.query.delete()
        Data.query.delete()
        
    with codecs.open(os.path.join(DATA_DIR, 'address.csv'), 'r', 'cp932') as f:
        for i, line in enumerate(f):
            if not i:
                continue
            l = line.strip().split(',')
            name = l[2]
            if l[3]:
                firstname2 = l[3]
            else:
                firstname2 = None
            yomi = l[4]
            zipcode = l[5]
            prefecture = l[6]
            address1 = l[7]
            address2 = l[8]
            tel = l[9]
            fax = l[10]
            mail = l[11]
            note = l[13]
            
            query = db_session.query(Data)\
                    .filter_by(name=name,address1=address1).first()
            if query:
                print ('%s exists' % query)

            data = Data()
            data.name = name
            if firstname2:
                data.firstname2 = firstname2
                if not data.title2:
                    data.title2 = PERSONAL_TITLE_LIST[0]
            data.yomi = yomi
            data.title = PERSONAL_TITLE_LIST[0]
            data.zipcode = zipcode
            if zipcode:
                if zipcode.find('-') == -1:
                    data.abroad = True
            data.prefecture = prefecture
            data.address1 = address1
            data.address2 = address2
            data.tel = tel
            data.fax = fax
            data.mail = mail
            data.note = note
                
            db_session.add(data)
            db_session.commit()

            # nenga
            nenga = Nenga()
            nenga.year = year
            nenga.data_id = data.id
            
            send = l[0]
            recieve = l[1]

            if send == '1':
                nenga.send = True
            if recieve not in ('', '00', '0'):
                nenga.receive = True

            db_session.add(nenga)
            db_session.commit()

def export_hagakisakka(year, output='sakka.csv'):
    title = ('氏名', 'ふりがな', '敬称', 'グループ', '郵便番号', '住所 1', '住所 2', '電話番号', 'FAX番号', '携帯電話番号', 'メール 1', 'メール 2', 'ホームページ', '備考', '家族 1 名前', '家族 1 ふりがな', '家族 1 敬称', '家族 2 名前', '家族 2 ふりがな', '家族 2 敬称', '家族 3 名前', '家族 3 ふりがな', '家族 3 敬称', '家族 4 名前', '家族 4 ふりがな', '家族 4 敬称', '家族 5 名前', '家族 5 ふりがな', '家族 5 敬称')

    data = [title]
    for x in db_session.query(Data).filter_by(invalid=False)\
            .filter_by(abroad=False).join(Nenga).filter(Nenga.year==year):
        row = (x.name, x.yomi, x.title, '', x.zipcode, x.address1,
               x.address2, x.tel, x.fax, x.mobile, x.mail, '', '', x.note,
               x.firstname2, '', x.title2, x.firstname3, '', x.title3,
               x.firstname4, '', x.title4, x.firstname5, '', x.title5)
        data.append(row)
    if len(data) == 1:
        return

    with open(os.path.join(DATA_DIR, output), 'w', newline='',
              encoding='cp932') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)

def add_new_year_data(year, before=None):
    if not before:
        before = db_session.query(func.max(Nenga.year)).first()[0]
    for x in db_session.query(Data).filter_by(invalid=False)\
            .join(Nenga).filter(Nenga.year==before):
        nenga_list = x.nenga
        nenga = Nenga()
        nenga.data_id = x.id
        nenga.year = year
        name = x.name
        try:
            db_session.add(nenga)
            nenga_list.append(nenga)
            x.nenga = nenga_list
            db_session.commit()
            print ('add %s, %s' % (name, year))
        except:
            db_session.rollback()
            print ('%s, %s data exists' % (name, year))

def check_args():
    parser = OptionParser()
    parser.add_option('-y',
                      '--year',
                      type='int',
                      metavar='N',
                      dest='year',
                      help='year N')
    parser.add_option('-i',
                      '--init',
                      action='store_true',
                      default=False)    
    parser.add_option('-m',
                      '--mode',
                      type='choice',
                      choices=['import', 'add', 'export'],
                      dest='mode',
                      default='export',
                      help='MODE import, add, export')
    (options, args) = parser.parse_args()

    if not options.year:
        parser.error('set year')
    return options, args

def main():
    options, args = check_args()
    year = options.year
    if options.mode == 'import':
        import_data_from_csv(year, init=options.init)
    elif options.mode == 'add':
        add_new_year_data(year)
    else:
        export_hagakisakka(year)

if __name__ == "__main__":
    main()
