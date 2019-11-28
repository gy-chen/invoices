import collections

Invoice = collections.namedtuple("Invoice", "id year month number note")


class InvoiceModel:
    def add_invoice(self, year, month, number, note):
        return NotImplemented

    def get_last_added_invoice_id(self):
        return NotImplemented

    def update_invoice(self, invoice):
        return NotImplemented

    def delete_invoice(self, id):
        return NotImplemented

    def get_invoices(self):
        return NotImplemented
