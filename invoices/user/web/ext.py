import collections
from flask import current_app
from invoices.user.web.sqlalchemy_model import UserModel

_UserModelExtConfig = collections.namedtuple("UserModelExtConfig", "session user_model")


class UserModelExt:
    def __init__(self, app=None, session=None):
        self._app = app
        self._session = session
        if self._app is not None:
            self.init_app(app, session)

    def init_app(self, app, session=None):
        user_model = UserModel(session)
        app.extensions["user_model_ext"] = _UserModelExtConfig(session, user_model)

    @property
    def app(self):
        if self._app is not None:
            return self._app
        return current_app

    @property
    def session(self):
        return self.app.extensions["user_model_ext"].session

    @property
    def user_model(self):
        return self.app.extensions["user_model_ext"].user_model


user_model_ext = UserModelExt()
