#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.sql.functions import max
from prizesgetter import PrizesGetter
from prizesparser import PrizesParser

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
    # whether or not this invoice is matched. None indices unknown.
    is_matched = Column(Boolean)
    # matched prize, usually None...
    prize_id = Column(Integer, ForeignKey('prizes.id'))
    prize = relationship('Prize', backref=backref('invoices'))

    def __repr__(self):
        parameters = {
            'year': self.year,
            'month': self.month,
            'number': self.number,
            'note': self.note,
            'is_matched': self.is_matched,
            'prize_id': self.prize_id
            }
        return self.__class__.__name__ + '(year={year}, month={month}, number={number}, note={note}, is_matched={is_matched}, prize_id={prize_id})'.format(**parameters)


class Prize(Base):
    __tablename__ = 'prizes'
    __table_args__ = (
        UniqueConstraint('year', 'month', 'number', 'type'),
        )
    id = Column(Integer, primary_key=True)
    # the date is same as Invoice's
    year = Column(Integer)
    month = Column(Integer)
    # prize's match number
    number = Column(String)
    # prize's type
    type_ = Column('type', Integer)

    def __repr__(self):
        parameters = {
            'id': self.id,
            'year': self.year,
            'month': self.month,
            'number': self.number,
            'type_': self.type_
            }
        return self.__class__.__name__ + '(year={year}, month={month}, number={number}, type_={type_}, id={id})'.format(**parameters)


class App(Base):
    '''App

    Store informations of the application.
    Don't instance this class directly, use method get_instance get get shared
    App instance.
    '''
    __tablename__ = 'appcore'

    id = Column(Integer, primary_key=True)
    prizes_last_modified_date = Column(DateTime)

    @classmethod
    def get_instance(cls):
        instance = session.query(cls).first()
        if not instance:
            instance = cls()
        return instance

    def update_prizes(self):
        getter = PrizesGetter()
        # check the modified date
        last_modified_date = getter.get_last_modified_date()
        if self.prizes_last_modified_date is not None\
            and last_modified_date <= self.prizes_last_modified_date:
            return
        # update current prizes
        parser = PrizesParser(getter.get_page_content())
        current_prizes = parser.get_current_prizes()
        current_year = parser.get_current_prizes_year()
        current_month = parser.get_current_prizes_month()
        for current_prize in current_prizes:
            conditions = {
                'year': current_year,
                'month': current_month,
                'number': current_prize.get_number(),
                'type_': current_prize.get_type()
                }
            if not session.query(Prize).filter_by(**conditions).first():
                new_prize = Prize(**conditions)
                session.add(new_prize)
        # update previous prizes
        previous_prizes = parser.get_previous_prizes()
        previous_year = parser.get_previous_prizes_year()
        previous_month = parser.get_previous_prizes_month()
        for previous_prize in previous_prizes:
            conditions = {
                'year': previous_year,
                'month': previous_month,
                'number': previous_prize.get_number(),
                'type_': previous_prize.get_type()
                }
            if not session.query(Prize).filter_by(**conditions).first():
                new_prize = Prize(**conditions)
                session.add(new_prize)
        # update last modified date
        session.add(self)
        self.prizes_last_modified_date = last_modified_date
        session.commit()

    def match_prizes(self):
        # fetch all stored prizes
        # order by the type of prizes to match the biggest prize first
        prizes = session.query(Prize).order_by(Prize.type_).all()
        # fetch all uncheck invoices
        invoices = session.query(Invoice).filter_by(is_matched=None).all()
        # start to match
        for invoice in invoices:
            for prize in prizes:
                # continue to next prize if year and month not matched
                if prize.year != invoice.year or prize.month != invoice.month:
                    continue
                # assume no match first
                invoice.is_matched = False
                # if match
                if invoice.number and invoice.number.endswith(prize.number):
                    invoice.is_matched = True
                    invoice.prize_id = prize.id
                    break
            session.add(invoice)
        # deal with the invoices that are too old
        min_year, min_month = session.query(Prize.year, Prize.month).order_by(Prize.year, Prize.month).first()
        if min_year is not None:
            assert min_month is not None
            session.query(Invoice).filter(and_(Invoice.year <= min_year, Invoice.month < min_month)).update({'is_matched': False})
        session.commit()

    def get_matched_invoices(self):
        """Get the matched invoices

        Get the list of matched invoice and sort by date

        () -> query
        """
        return session.query(Invoice).filter_by(is_matched=True).order_by(Invoice.year, Invoice.month)

    def get_no_matched_invoices(self):
        """Get the no matched invoices

        The invoices this method return can be thrown into the trash bin.
        () -> query
        """
        return session.query(Invoice).filter_by(is_matched=False).order_by(Invoice.year, Invoice.month)

    def get_non_matched_invoices(self):
        """Get the invoices that not check before.

        These invoices are waiting for new prizes information.
        () -> query
        """
        return session.query(Invoice).filter_by(is_matched=None).order_by(Invoice.year, Invoice.month)
