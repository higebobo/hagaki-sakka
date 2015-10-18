#!/usr/bin/env python
# -*- mode: python -*- -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import SQLALCHEMY_DATABASE_URI, ECHO

engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True,
                       echo=ECHO)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def create_db():
    Base.metadata.create_all(bind=engine)
