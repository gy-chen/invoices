from invoices.invoice.sqlalchemy_model import InvoiceModel as CoreInvoiceModel
from invoices.invoice.model import Invoice
from invoices.user_invoice.web.model import UserInvoiceModel as SharedUserInvoiceModel
from invoices.user_invoice.sqlalchemy_model import UserInvoiceModel as CoreUserInvoiceModel
from invoices.user_invoice_match.sqlalchemy_model import UserInvoiceMatchModel as CoreUserInvoiceMatchModel

class UserInvoiceModel(SharedUserInvoiceModel):
    def __init__(self, session):
        self._session = session
        self._core_invoice_model = CoreInvoiceModel(session)
        self._core_user_invoice_model = CoreUserInvoiceModel(session)
        self._core_user_invoice_match_model = CoreUserInvoiceMatchModel(session)

    def add_invoice(self, user_sub, year, month, number, note):
        self._core_invoice_model.add_invoice(year, month, number, note)
        self._session.commit()
        invoice_id = self._core_invoice_model.get_last_added_invoice_id()
        self._core_user_invoice_model.add_user_invoice(user_sub, invoice_id)
        self._session.commit()
        return Invoice(invoice_id, year, month, number, note)

    def update_invoice(self, user_sub, id, year, month, number, note):
        # TODO valid invoice's user
        invoice = Invoice(id, year, month, number, note)
        self._core_invoice_model.update_invoice(invoice)
        self._session.commit()
        return invoice

    def delete_invoice(self, user_sub, id):
        # TODO valid invoice's user
        self._core_invoice_model.delete_invoice(id)

    def get_user_invoices(self, user_sub, offset, per_page):
        return self._core_user_invoice_model.get_user_invoices(user_sub, offset, per_page)

    def get_processed_user_invoices(self, user_sub, offset, per_page):
        return self._core_user_invoice_match_model.get_invoice_matches(user_sub, offset, per_page)