from sqlalchemy import Column, Integer, String, Enum
from invoices.sqlalchemy import Base
from invoices.common import Month
from invoices.invoice.model import Invoice as SharedInvoice
from invoices.invoice.model import InvoiceModel as SharedInvoiceModel


class ModelAdapter:
    def to_invoice(self, invoice):
        return SharedInvoice(*invoice)


class Invoice(Base):
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


class InvoiceModel(SharedInvoiceModel):
    def __init__(self, session):
        self._session = session
        self._model_adapter = ModelAdapter()
        self._last_added_invoice = None

    def add_invoice(self, year, month, number, note):
        invoice_model = Invoice(None, year, month, number, note)
        self._session.add(invoice_model)
        self._last_added_invoice = invoice_model

    def get_last_added_invoice_id(self):
        return self._last_added_invoice.id

    def update_invoice(self, invoice):
        invoice_model = self._session.query(Invoice).get(invoice.id)
        if not invoice_model:
            raise ValueError("the invoice is not exists")
        invoice_model.year = invoice.year
        invoice_model.month = invoice.month
        invoice_model.number = invoice.number
        invoice_model.note = invoice.note
        self._session.add(invoice_model)

    def delete_invoice(self, id):
        invoice_model = self._session.query(Invoice).get(id)
        if not invoice_model:
            raise ValueError("the invoice is not exists")
        self._session.delete(invoice_model)

    def get_invoices(self):
        invoice_models = self._session.query(Invoice).all()
        return list(map(self._model_adapter.to_invoice, invoice_models))
