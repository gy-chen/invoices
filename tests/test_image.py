import base64
import os
import pytest
from invoices.image.util import decode_base64_image

BASE_PATH = os.path.dirname(__file__)


@pytest.fixture
def sample1():
    path = os.path.join(BASE_PATH, "sample/invoice1.jpg")
    img_base64 = base64.b64encode(open(path, "rb").read())
    return f"data:image/jpg;base64.{img_base64.decode()}"


def test_decode_base64_image(sample1):
    decode_base64_image(sample1)
