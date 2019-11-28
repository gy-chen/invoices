import collections

UserInvoiceMatch = collections.namedtuple("UserInvoiceMatch", "user invoice_match")


class UserInvoiceMatchModel:
    def get_invoice_matches(self, user_sub, offset, per_page):
        return NotImplemented
