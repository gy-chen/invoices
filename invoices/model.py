import collections
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKeyConstraint
from invoices.common import PrizeType, Month

Invoice = collections.namedtuple("Invoice", "id year month number note")
Prize = collections.namedtuple("Prize", "type year month number prize")
InvoiceMatch = collections.namedtuple("InvoiceMatch", "invoice prize is_matched")
User = collections.namedtuple("User", "sub email")
UserInvoice = collections.namedtuple("UserInvoice", "user invoice")
UserInvoiceMatch = collections.namedtuple("UserInvoiceMatch", "user invoice_match")

Base = declarative_base()


class _ModelAdapter:
    def __init__(self, session):
        self._session = session

    def to_invoice_match(self, invoice_match_model):
        invoice_model = self._session.query(_Invoice).get(
            invoice_match_model.invoice_id
        )
        prize_model = None
        if (
            invoice_match_model.prize_type
            and invoice_match_model.prize_year
            and invoice_match_model.prize_type
        ):
            prize_model = self._session.query(_Prize).get(
                (
                    invoice_match_model.prize_type,
                    invoice_match_model.prize_year,
                    invoice_match_model.prize_month,
                )
            )
        return InvoiceMatch(
            self.to_invoice(invoice_model),
            prize_model and self.to_prize(prize_model),
            prize_model is not None,
        )

    def to_invoice(self, invoice_model):
        return Invoice(*invoice_model)

    def to_prize(self, prize_model):
        return Prize(*prize_model)

    def to_user(self, user_model):
        return User(*user_model)

    def to_user_invoice(self, user_invoice_model):
        user_model = self._session.query(_User).get(user_invoice_model.user_sub)
        user = self.to_user(user_model)

        invoice_model = self._session.query(_Invoice).get(user_invoice_model.invoice_id)
        invoice = self.to_invoice(invoice_model)

        return UserInvoice(user, invoice)

    def to_user_invoice_match(self, user_model, invoice_match_model):
        user = self.to_user(user_model)
        invoice_match = self.to_invoice_match(invoice_match_model)
        return UserInvoiceMatch(user, invoice_match)


class _Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Enum(Month))
    number = Column(String)
    note = Column(String)

    def __init__(self, id, year, month, number, note):
        self.id = id
        self.year = year
        self.month = month
        self.number = number
        self.note = note

    def __iter__(self):
        yield from (self.id, self.year, self.month, self.number, self.note)


class _Prize(Base):
    __tablename__ = "prizes"

    type = Column(Enum(PrizeType), primary_key=True)
    year = Column(Integer, primary_key=True)
    month = Column(Enum(Month), primary_key=True)
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


class _InvoiceMatch(Base):
    __tablename__ = "invoicematches"

    invoice_id = Column(Integer, ForeignKey("invoices.id"), primary_key=True)
    prize_type = Column(Enum(PrizeType))
    prize_year = Column(Integer)
    prize_month = Column(Enum(Month))

    __table_args__ = (
        ForeignKeyConstraint(
            ["prize_type", "prize_year", "prize_month"],
            ["prizes.type", "prizes.year", "prizes.month"],
        ),
    )

    def __init__(self, invoice_id, prize_type, prize_year, prize_month):
        self.invoice_id = invoice_id
        self.prize_type = prize_type
        self.prize_year = prize_year
        self.prize_month = prize_month

    def __iter__(self):
        yield from (self.invoice_id, self.prize_type, self.prize_year, self.prize_month)


class _User(Base):
    __tablename__ = "users"

    sub = Column(String, primary_key=True)
    email = Column(String)

    def __init__(self, sub, email):
        self.sub = sub
        self.email = email

    def __iter__(self):
        yield from (self.sub, self.email)


class _UserInvoice(Base):
    __tablename__ = "user_invoice"

    user_sub = Column(String, ForeignKey("users.sub"), primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), primary_key=True)

    def __init__(self, user_sub, invoice_id):
        self.user_sub = user_sub
        self.invoice_id = invoice_id

    def __iter__(self):
        yield from (self.user_sub, self.invoice_id)


class InvoiceModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = _ModelAdapter(session)
        self._last_added_invoice = None

    def add_invoice(self, year, month, number, note):
        invoice_model = _Invoice(None, year, month, number, note)
        self._session.add(invoice_model)
        self._last_added_invoice = invoice_model

    def get_last_added_invoice_id(self):
        return self._last_added_invoice.id

    def update_invoice(self, invoice):
        invoice_model = self._session.query(_Invoice).get(invoice.id)
        if not invoice_model:
            raise ValueError("the invoice is not exists")
        invoice_model.year = invoice.year
        invoice_model.month = invoice.month
        invoice_model.number = invoice.number
        invoice_model.note = invoice.note
        self._session.add(invoice_model)

    def delete_invoice(self, id):
        invoice_model = self._session.query(_Invoice).get(id)
        if not invoice_model:
            raise ValueError("the invoice is not exists")
        self._session.delete(invoice_model)

    def get_invoices(self):
        invoice_models = self._session.query(_Invoice).all()
        return list(map(self._model_adapter.to_invoice, invoice_models))


class PrizeModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = _ModelAdapter(session)

    def add_prize(self, type, year, month, number, prize):
        prize_model = _Prize(type, year, month, number, prize)
        self._session.add(prize_model)

    def delete_prize(self, type_, year, month):
        prize_model = self._session.query(_Prize).get((type_, year, month))
        if not prize_model:
            raise ValueError("prize is not exists")
        self._session.delete(prize_model)

    def get_prizes(self):
        prize_models = self._session.query(_Prize).all()
        return list(map(self._model_adapter.to_prize, prize_models))


class InvoiceMatchModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = _ModelAdapter(session)

    def add_invoice_match(self, invoice_id, prize_type, prize_year, prize_month):
        invoice_match_model = _InvoiceMatch(
            invoice_id, prize_type, prize_year, prize_month
        )
        self._session.add(invoice_match_model)

    def add_invoice_unmatch(self, invoice_id):
        invoice_match_model = _InvoiceMatch(
            invoice_id, None, None, None
        )
        self._session.add(invoice_match_model)

    def get_invoice_matches(self):
        invoice_match_models = self._session.query(_InvoiceMatch).all()
        return list(map(self._model_adapter.to_invoice_match, invoice_match_models))

    def get_unprocess_invoices(self):
        invoice_models = (
            self._session.query(_Invoice)
            .outerjoin(_InvoiceMatch, _Invoice.id == _InvoiceMatch.invoice_id)
            .filter(_InvoiceMatch.invoice_id == None)
            .all()
        )
        return list(map(self._model_adapter.to_invoice, invoice_models))


class UserModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = _ModelAdapter(session)

    def register_user(self, user):
        user_model = _User(*user)
        self._session.add(user_model)

    def get_user(self, sub):
        user = self._session.query(_User).get(sub)
        if not user:
            return None
        return self._model_adapter.to_user(user)


class UserInvoiceModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = _ModelAdapter(session)

    def add_user_invoice(self, user_sub, invoice_id):
        user_invoice = _UserInvoice(user_sub, invoice_id)
        self._session.add(user_invoice)

    def get_user_invoices(self, user_sub, offset, per_page):
        user_invoice_models = (
            self._session.query(_UserInvoice).limit(per_page).offset(offset).all()
        )
        return list(map(self._model_adapter.to_user_invoice, user_invoice_models))


class UserInvoiceMatchModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = _ModelAdapter(session)

    def get_invoice_matches(self, user_sub, offset, per_page):
        result = []
        for user_model, _, _, invoice_match_model in (
            self._session.query(_User, _UserInvoice, _Invoice, _InvoiceMatch)
            .filter(_User.sub == _UserInvoice.user_sub)
            .filter(_UserInvoice.invoice_id == _Invoice.id)
            .filter(_Invoice.id == _InvoiceMatch.invoice_id)
            .filter(_User.sub == user_sub)
            .limit(per_page)
            .offset(offset)
            .all()
        ):
            result.append(
                self._model_adapter.to_user_invoice_match(
                    user_model, invoice_match_model
                )
            )
        return result
