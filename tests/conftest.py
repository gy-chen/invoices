import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoices.model import Base


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

