import uwsgi
import json
from invoices.image.util import decode_base64_image
from invoices.qrcode import scan


def create_app():
    def application(env, start_response):
        uwsgi.websocket_handshake()
        while True:
            msg_raw = uwsgi.websocket_recv()
            base64_content = msg_raw.decode()
            try:
                img = decode_base64_image(base64_content)
            except ValueError:
                continue
            for invoice in scan(img):
                uwsgi.websocket_send(
                    json.dumps(
                        {
                            "year": invoice.year,
                            "month": invoice.month,
                            "number": invoice.number,
                            "prefix": invoice.prefix,
                        }
                    ).encode()
                )

    return application
