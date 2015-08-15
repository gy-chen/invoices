#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref

__ALL__ = ['Invoice', 'Prize']
# TODO put configures in a seperate file.
engine = create_engine('sqlite:///invoices.db', echo=False) # use echo to turn the debug information on or off.
Base = declarative_base()
Session = sessionmaker(bind=engine) # or Session.configure(bind=engine)
session = Session()
# create db using
# Base.metadata.create_all(engine)
# or...
# Invoice.__table__.create(engine)
# Prize.__table__.create(engine)


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    # year, in Taiwan year
    year = Column(Integer)
    # month, range from 1 to 6.
    month = Column(Integer)
    # number of a invoice
    number = Column(String)
    # note for helping remembering the invoice's identfication.
    note = Column(String)
    # matched prize, usually None...
    prize_id = Column(Integer, ForeignKey('prizes.id'))
    prize = relationship('Prize', backref=backref('invoices'))


class Prize(Base):
    __tablename__ = 'prizes'

    id = Column(Integer, primary_key=True)
    # the date is same as Invoice's
    year = Column(Integer)
    month = Column(Integer)
    # prize's match number
    number = Column(String)
    # prize's type
    type_ = Column(Integer)
