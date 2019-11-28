import collections


InvoiceMatch = collections.namedtuple("InvoiceMatch", "invoice prize is_matched")


class InvoiceMatchModel:
    def add_invoice_match(
        self, invoice_id, prize_type, prize_year, prize_month, prize_number
    ):
        return NotImplemented

    def add_invoice_unmatch(self, invoice_id):
        return NotImplemented

    def get_invoice_matches(self):
        return NotImplemented

    def get_unprocess_invoices(self):
        return NotImplemented
