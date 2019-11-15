from flask import Blueprint

bp = Blueprint("qrcode", __name__)


@bp.route("/scan")
def scan():
    headers = {"X-Offload-QrCode-Scan": 1}
    return ("", headers)

