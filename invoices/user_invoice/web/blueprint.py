from flask import abort
from flask import request
from flask import Blueprint
from flask import jsonify
from werkzeug.datastructures import MultiDict
from invoices.login.web import required_login, current_user
from invoices.user_invoice.web.ext import user_invoice_model_ext
from invoices.user_invoice.web.form import AddInvoiceForm
from invoices.user_invoice.web.form import UpdateInvoiceForm
from invoices.user_invoice.web.form import GetInvoicesForm
from invoices.user_invoice.web.form import GetProcessedInvoicesForm

bp = Blueprint("user_invoices", __name__)


@bp.route("/invoice", methods=["POST"])
@required_login
def add_invoice():
    add_invoice_form = AddInvoiceForm()
    if add_invoice_form.validate():
        invoice = user_invoice_model_ext.user_invoice_model.add_invoice(
            current_user.sub, *add_invoice_form
        )
        return jsonify(invoice_id=invoice.id)
    abort(400)


@bp.route("/invoice/<int:id>", methods=["PUT"])
@required_login
def update_invoice(id):
    mixed_data = MultiDict(request.form)
    mixed_data.update({"id": id})
    update_invoice_form = UpdateInvoiceForm(mixed_data)
    if update_invoice_form.validate():
        try:
            user_invoice_model_ext.user_invoice_model.update_invoice(
                current_user.sub, *update_invoice_form
            )
        except ValueError:
            abort(400)
        return ("", 204)
    abort(400)


@bp.route("/invoice/<int:id>", methods=["DELETE"])
@required_login
def delete_invoice(id):
    try:
        user_invoice_model_ext.user_invoice_model.delete_invoice(current_user.sub, id)
    except ValueError:
        abort(400)
    return ("", 204)


@bp.route("/invoices", methods=["GET"])
@required_login
def get_invoices():
    get_invoices_form = GetInvoicesForm()
    if not get_invoices_form.validate():
        abort(400)
    offset, per_page = get_invoices_form.offset.data, get_invoices_form.per_page.data
    user_invoices = user_invoice_model_ext.user_invoice_model.get_user_invoices(
        current_user.sub, offset, per_page
    )
    return jsonify(invoices=list(map(_user_invoice_to_output_dict, user_invoices)))


@bp.route("/invoices/processed")
@required_login
def get_processed_invoices():
    get_processed_invoices_form = GetProcessedInvoicesForm()
    if not get_processed_invoices_form.validate():
        abort(400)
    offset, per_page = (
        get_processed_invoices_form.offset,
        get_processed_invoices_form.per_page,
    )
    user_invoice_matches = user_invoice_model_ext.user_invoice_model.get_invoice_matches(
        current_user.sub, offset, per_page
    )
    return jsonify(
        matches=list(map(_user_invoice_match_to_output_dict, user_invoice_matches))
    )


def _invoice_to_output_dict(invoice):
    return {
        "id": invoice.id,
        "year": invoice.year,
        "month": invoice.month.value,
        "number": invoice.number,
        "note": invoice.note,
    }


def _user_invoice_to_output_dict(user_invoice):
    return _invoice_to_output_dict(user_invoice.invoice)


def _user_invoice_match_to_output_dict(user_invoice_match):
    return {
        "invoice": _invoice_to_output_dict(user_invoice_match.invoice),
        "is_matched": user_invoice_match.invoice_match.is_matched,
    }
