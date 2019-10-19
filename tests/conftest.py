import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoices.model import Base
from invoices.web import create_app


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

    app = create_app(TestConfig)
    with app.app_context():
        yield app
