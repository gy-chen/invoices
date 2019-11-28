from invoices.user.web.model import UserModel as SharedUserModel
from invoices.user.model import User
from invoices.user.sqlalchemy_model import UserModel as CoreUserModel


class UserModel(SharedUserModel):
    def __init__(self, session):
        self._session = session
        self._core_user_model = CoreUserModel(session)

    def register_user(self, user_sub, email):
        user = User(user_sub, email)
        self._core_user_model.register_user(user)
        self._session.commit()
        return user

    def load_user(self, user_sub):
        return self._core_user_model.get_user(user_sub)
