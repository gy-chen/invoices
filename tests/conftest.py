import pytest
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoices.user.model import User
from invoices.user.web.ext import user_model_ext
from invoices.app import create_app
from invoices.app import db
from invoices.sqlalchemy import Base


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.fixture
def app():
    class TestConfig:
        WTF_CSRF_ENABLED = False
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        TESTING = True

    app = create_app(TestConfig)
    with app.app_context():
        Base.metadata.create_all(db.engine)
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def logged_in_user(app):
    user = user_model_ext.user_model.register_user("test_sub", "test@example.org")
    g.current_user = user
