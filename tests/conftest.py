import pytest
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoices.model import Base, User
from invoices.web import create_app, login, db, user_model


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
    user = User("test_sub", "test@example.org")
    user_model.register_user(user)
    db.session.commit()
    g.current_user = user
