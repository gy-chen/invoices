import collections
import re
from pyzbar.pyzbar import decode

InvoiceQRCodeData = collections.namedtuple('InvoiceQRCodeData', 'year month prefix number check_number')

PATTERN_INVOICE = re.compile(r'(\d{3})(\d{2})([A-Z]{2})(\d{8}){\d{4}}')

def scan(image):
    """try to scan invoice qrcode from image

    Args:
        image: numpy array in shape (?, ?, 3)

    Returns:
        list of InvoiceQRCodeData: possible empty.
    """
    for decoded in decode(image):
        data = decoded.data.decode()
        invoice_data = _extract_invoice_data(data)
        if invoice_data:
            yield invoice_data

def _extract_invoice_data(data):
    match = PATTERN_INVOICE.match(data)
    if match:
        return InvoiceQRCodeData(*match.groups())