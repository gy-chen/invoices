from invoices.user.sqlalchemy_model import User
from invoices.user.sqlalchemy_model import ModelAdapter as UserModelAdapter
from invoices.invoice.sqlalchemy_model import Invoice
from invoices.invoice_match.sqlalchemy_model import InvoiceMatch
from invoices.invoice_match.sqlalchemy_model import (
    ModelAdapter as InvoiceMatchModelAdapter,
)
from invoices.user_invoice.sqlalchemy_model import UserInvoice
from invoices.user_invoice_match.model import UserInvoiceMatch as SharedUserInvoiceMatch


class ModelAdapter:
    def __init__(self, session):
        self._session = session
        self._user_model_adapter = UserModelAdapter()
        self._invoice_match_model_adapter = InvoiceMatchModelAdapter(session)

    def to_user_invoice_match(self, user_model, invoice_match_model):
        user = self._user_model_adapter.to_user(user_model)
        invoice_match = self._invoice_match_model_adapter.to_invoice_match(
            invoice_match_model
        )
        return SharedUserInvoiceMatch(user, invoice_match)


class UserInvoiceMatchModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = ModelAdapter(session)

    def get_invoice_matches(self, user_sub, offset, per_page):
        result = []
        for user_model, invoice_match_model in (
            self._session.query(User, InvoiceMatch)
            .filter(User.sub == UserInvoice.user_sub)
            .filter(UserInvoice.invoice_id == Invoice.id)
            .filter(Invoice.id == InvoiceMatch.invoice_id)
            .filter(User.sub == user_sub)
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
