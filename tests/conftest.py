import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoices.model import _Base as InvoiceModelBase


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=True)
    InvoiceModelBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

