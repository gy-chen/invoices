import collections

UserInvoice = collections.namedtuple("UserInvoice", "user invoice")


class UserInvoiceModel:
    def add_user_invoice(self, user_sub, invoice_id):
        return NotImplemented

    def get_user_invoices(self, user_sub, offset, per_page):
        return NotImplemented
