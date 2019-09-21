import collections
import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


class InvoiceMonthEnum(enum.Enum):
    MONTH_1_2 = 1
    MONTH_3_4 = 2
    MONTH_5_6 = 3
    MONTH_7_8 = 4
    MONTH_9_10 = 5
    MONTH_11_12 = 6


Invoice = collections.namedtuple("Invoice", "id year month number")
Prize = collections.namedtuple("Prize", "type_ year month number prize")
InvoiceMatch = collections.namedtuple(
    "InvoiceMatch", "invoice_id type_ year month prize is_matched"
)
User = collections.namedtuple("User", "sub email")

_Base = declarative_base()


class _Invoice(_Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Enum(InvoiceMonthEnum))
    number = Column(String)

    def __init__(self, id, year, month, number):
        self.id = id
        self.year = year
        self.month = month
        self.number = number

    def __iter__(self):
        yield from (self.id, self.year, self.month, self.number)


class InvoiceModel:
    def __init__(self, session):
        self._session = session

    def add_invoice(self, invoice):
        invoice_model = _Invoice(*invoice)
        self._session.add(invoice_model)

    def update_invoice(self, invoice):
        invoice_model = self._session.query(_Invoice).get(invoice.id)
        if not invoice_model:
            raise ValueError("the invoice is not exists")
        invoice_model.year = invoice.year
        invoice_model.month = invoice.month
        invoice_model.number = invoice.number
        self._session.add(invoice_model)

    def delete_invoice(self, id):
        invoice_model = self._session.query(_Invoice).get(id)
        if not invoice_model:
            raise ValueError("the invoice is not exists")
        self._session.delete(invoice_model)

    def get_invoices(self):
        return [Invoice(*invoice) for invoice in self._session.query(_Invoice).all()]


class _Prize(_Base):
    __tablename__ = "prizes"

    type = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)
    number = Column(String)
    prize = Column(Integer)

    def __init__(self, type, year, month, number, prize):
        self.type = type
        self.year = year
        self.month = month
        self.number = number
        self.prize = prize

    def __iter__(self):
        yield from (self.type, self.year, self.month, self.number, self.prize)


class PrizeModel:
    def add_prize(self, prize):
        pass

    def delete_prize(self, type_, year, month):
        pass

    def get_prizes(self):
        pass


class _InvoiceMatch(_Base):
    __tablename__ = "invoicematches"

    invoice_id = Column(Integer, ForeignKey("invoices.id"), primary_key=True)
    type = Column(Integer)
    year = Column(Integer)
    month = Column(Integer)
    is_matched = Column(Boolean)

    def __init__(self, invoice_id, type, year, month, is_matched):
        self.invoice_id = invoice_id
        self.type = type
        self.year = year
        self.month = month
        self.is_matched = is_matched

    def __iter__(self):
        yield from (self.invoice_id, self.type, self.year, self.month, self.is_matched)


class InvoiceMatchModel:
    def match_invoice(self, invoice_number, prize_number):
        pass

    def add_match_invoice(self, invoice_id, type_, year, month, is_matched):
        pass

    def get_matched_invoices(self):
        pass


class UserModel:
    def register_user(self, user):
        pass

    def get_user(self, sub):
        pass
