import os
import pytest
from PIL import Image
from invoices.qrcode import scan

BASE_PATH = os.path.dirname(__file__)


@pytest.fixture
def sample1():
    path = os.path.join(BASE_PATH, "sample/invoice1.jpg")
    return Image.open(path)


def test_qrcode(sample1):
    invoices = list(scan(sample1))
    assert len(invoices) == 1
