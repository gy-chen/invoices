import collections
import re
from pyzbar.pyzbar import decode

InvoiceQRCodeData = collections.namedtuple(
    "InvoiceQRCodeData", "year month prefix number"
)

PATTERN_INVOICE = re.compile(r"([A-Z]{2})(\d{8})(\d{3})(\d{2})")


def scan(image):
    """try to scan invoice qrcode from image

    Args:
        image: numpy array in shape (?, ?, 3)

    Returns:
        list of InvoiceQRCodeData: possible empty.
    """
    for decoded in decode(image):
        data = decoded.data.decode()
        yield from _extract_invoice_data(data)


def _extract_invoice_data(data):
    match = PATTERN_INVOICE.match(data)
    if match:
        prefix, number, year, month = match.groups()
        yield InvoiceQRCodeData(year, month, prefix, number)
