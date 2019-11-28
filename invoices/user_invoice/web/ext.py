import collections
from flask import current_app
from invoices.user_invoice.web.sqlalchemy_model import UserInvoiceModel

_UserInvoiceModelExtConfig = collections.namedtuple(
    "UserInvoiceModelExtConfig", "session user_invoice_model"
)


class UserInvoiceModelExt:
    def __init__(self, app=None, session=None):
        self._app = app
        self._session = session
        if app is not None:
            self.init_app(app)

    @property
    def app(self):
        if self._app is not None:
            return self._app
        return current_app

    @property
    def session(self):
        return self.app.extensions["user_invoice_ext"].session

    @property
    def user_invoice_model(self):
        return self.app.extensions["user_invoice_ext"].user_invoice_model

    def init_app(self, app, session=None):
        user_invoice_model = UserInvoiceModel(session)
        app.extensions["user_invoice_ext"] = _UserInvoiceModelExtConfig(
            session, user_invoice_model
        )


user_invoice_model_ext = UserInvoiceModelExt()
