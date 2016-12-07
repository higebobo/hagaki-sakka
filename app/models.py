#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, \
     Text, Boolean
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref

from config import DATABASE_PREFIX
from .database import Base

class Data(Base):
    __tablename__ = '%s_data' % DATABASE_PREFIX
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    yomi = Column(String(20))
    title = Column(String(10))
    zipcode = Column(String(10))
    prefecture = Column(String(10))
    address1 = Column(String(50))
    address2 = Column(String(50))
    tel = Column(String(20))
    fax = Column(String(20))
    mail = Column(String(100))
    mobile = Column(String(100))
    firstname2 = Column(String(20))
    title2 = Column(String(10))
    mail2 = Column(String(100))
    mobile2 = Column(String(100))
    firstname3 = Column(String(20))
    title3 = Column(String(10))
    mail3 = Column(String(100))
    mobile3 = Column(String(100))
    firstname4 = Column(String(20))
    title4 = Column(String(10))
    mail4 = Column(String(100))
    mobile4 = Column(String(100))
    firstname5 = Column(String(20))
    title5 = Column(String(10))
    mail5 = Column(String(100))
    mobile5 = Column(String(100))
    note = Column(Text)
    abroad = Column(Boolean, default=False)
    invalid = Column(Boolean, default=False)
    nenga = relationship("Nenga", backref='data',
                         cascade='all, delete-orphan')
    sender = Column(String(10))
    updatetime = Column(DateTime, default=datetime.datetime.now())
    
    def __repr__(self):
        return "<Data(%r)>" % self.name

class Nenga(Base):
    __tablename__ = '%s_nenga' % DATABASE_PREFIX
    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    send = Column(Boolean, default=False)
    receive = Column(Boolean, default=False)
    mourning = Column(Boolean, default=False)
    address_unknown = Column(Boolean, default=False)
    note = Column(Text)
    data_id = Column(Integer, ForeignKey('%s_data.id'%DATABASE_PREFIX))
    
    __table_args__ = (UniqueConstraint(year, data_id),)
    
    def __repr__(self):
        return "<Nenga(%s, %r)>" % (self.year, self.data.name)
