from sqlalchemy import Column, String
from invoices.sqlalchemy import Base
from invoices.user.model import User as SharedUser
from invoices.user.model import UserModel as SharedUserModel


class ModelAdapter:
    def to_user(self, user):
        return SharedUser(*user)


class User(Base):
    __tablename__ = "users"

    sub = Column(String, primary_key=True)
    email = Column(String)

    def __init__(self, sub, email):
        self.sub = sub
        self.email = email

    def __iter__(self):
        yield from (self.sub, self.email)


class UserModel(SharedUserModel):
    def __init__(self, session):
        self._session = session
        self._model_adapter = ModelAdapter()

    def register_user(self, user):
        user_model = User(*user)
        self._session.merge(user_model)

    def get_user(self, sub):
        user = self._session.query(User).get(sub)
        if not user:
            return None
        return self._model_adapter.to_user(user)
