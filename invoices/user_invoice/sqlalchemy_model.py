from sqlalchemy import Column, Integer, String, ForeignKey
from invoices.sqlalchemy import Base
from invoices.user.sqlalchemy_model import ModelAdapter as UserModelAdapter
from invoices.user.sqlalchemy_model import User
from invoices.invoice.sqlalchemy_model import ModelAdapter as InvoiceModelAdapter
from invoices.invoice.sqlalchemy_model import Invoice
from invoices.user_invoice.model import UserInvoice as SharedUserInvoice
from invoices.user_invoice.model import UserInvoiceModel as SharedUserInvoiceModel


class ModelAdapter:
    def __init__(self, session):
        self._session = session
        self._user_model_adapter = UserModelAdapter()
        self._invoice_model_adapter = InvoiceModelAdapter()

    def to_user_invoice(self, user_invoice):
        user_model = self._session.query(User).get(user_invoice.user_sub)
        user = self._user_model_adapter.to_user(user_model)

        invoice_model = self._session.query(Invoice).get(user_invoice.invoice_id)
        invoice = self._invoice_model_adapter.to_invoice(invoice_model)

        return SharedUserInvoice(user, invoice)


class UserInvoice(Base):
    __tablename__ = "user_invoice"

    user_sub = Column(String, ForeignKey("users.sub"), primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), primary_key=True)

    def __init__(self, user_sub, invoice_id):
        self.user_sub = user_sub
        self.invoice_id = invoice_id

    def __iter__(self):
        yield from (self.user_sub, self.invoice_id)


class UserInvoiceModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = ModelAdapter(session)

    def add_user_invoice(self, user_sub, invoice_id):
        user_invoice = UserInvoice(user_sub, invoice_id)
        self._session.add(user_invoice)

    def get_user_invoices(self, user_sub, offset, per_page):
        user_invoice_models = (
            self._session.query(UserInvoice).limit(per_page).offset(offset).all()
        )
        return list(map(self._model_adapter.to_user_invoice, user_invoice_models))
