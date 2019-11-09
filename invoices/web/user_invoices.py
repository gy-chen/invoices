from flask import Blueprint, abort, jsonify, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length
from werkzeug.datastructures import MultiDict
from invoices.web.login import required_login, current_user
from invoices.web import db, invoice_model, user_invoice_model, user_invoice_match_model
from invoices.model import Invoice, UserInvoiceMatch
from invoices.common import Month

bp = Blueprint("user_invoices", __name__)


def _month_to_enum(month):
    month_map = {
        1: Month.MONTH_1_2,
        2: Month.MONTH_3_4,
        3: Month.MONTH_5_6,
        4: Month.MONTH_7_8,
        5: Month.MONTH_9_10,
        6: Month.MONTH_11_12,
    }
    return month_map[month]


class AddInvoiceForm(FlaskForm):
    year = IntegerField("year", validators=[DataRequired(), NumberRange(100, 200)])
    month = IntegerField("month", validators=[DataRequired(), NumberRange(1, 6)])
    number = StringField("number", validators=[DataRequired(), Length(8, 8)])
    note = StringField("note", default="")

    def to_add_invoice_args(self):
        return (
            self.year.data,
            _month_to_enum(self.month.data),
            self.number.data,
            self.note.data,
        )


@bp.route("/invoice", methods=["POST"])
@required_login
def add_invoice():
    add_invoice_form = AddInvoiceForm()
    if add_invoice_form.validate():
        invoice = add_invoice_form.to_add_invoice_args()
        invoice_model.add_invoice(*invoice)
        db.session.commit()
        invoice_id = invoice_model.get_last_added_invoice_id()
        user_invoice_model.add_user_invoice(current_user.sub, invoice_id)
        db.session.commit()
        return jsonify(invoice_id=invoice_id)
    abort(400)


class UpdateInvoiceForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()])
    year = IntegerField("year", validators=[DataRequired(), NumberRange(100, 200)])
    month = IntegerField("month", validators=[DataRequired(), NumberRange(1, 6)])
    number = StringField("number", validators=[DataRequired(), Length(8, 8)])
    note = StringField("note", validators=[DataRequired()])

    def to_update_invoice(self):
        return Invoice(
            self.id.data,
            self.year.data,
            _month_to_enum(self.month.data),
            self.number.data,
            self.note.data,
        )


@bp.route("/invoice/<int:id>", methods=["PUT"])
@required_login
def update_invoice(id):
    mixed_data = MultiDict(request.form)
    mixed_data.update({"id": id})
    update_invoice_form = UpdateInvoiceForm(mixed_data)
    if update_invoice_form.validate():
        update_invoice = update_invoice_form.to_update_invoice()
        try:
            invoice_model.update_invoice(update_invoice)
        except ValueError:
            abort(400)
        db.session.commit()
        return ("", 204)
    abort(400)


@bp.route("/invoice/<int:id>", methods=["DELETE"])
@required_login
def delete_invoice(id):
    try:
        invoice_model.delete_invoice(id)
        db.session.commit()
    except ValueError:
        abort(400)
    return ("", 204)


class GetInvoicesForm(FlaskForm):
    offset = IntegerField("offset", validators=[NumberRange(min=0)], default=0)
    per_page = IntegerField(
        "per_page", validators=[NumberRange(min=0, max=40)], default=20
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


@bp.route("/invoices", methods=["GET"])
@required_login
def get_invoices():
    get_invoices_form = GetInvoicesForm()
    if not get_invoices_form.validate():
        abort(400)
    user_invoices = user_invoice_model.get_user_invoices(
        current_user.sub, get_invoices_form.offset.data, get_invoices_form.per_page.data
    )
    return jsonify(invoices=list(map(_user_invoice_to_output_dict, user_invoices)))


class GetProcessedInvoicesForm(FlaskForm):
    offset = IntegerField("offset", validators=[NumberRange(min=0)], default=0)
    per_page = IntegerField(
        "per_page", validators=[NumberRange(min=0, max=40)], default=20
    )


def _user_invoice_match_to_output_dict(user_invoice_match):
    return {
        "invoice": _invoice_to_output_dict(user_invoice_match.invoice),
        "is_matched": user_invoice_match.invoice_match.is_matched,
    }


@bp.route("/invoices/processed")
@required_login
def get_processed_invoices():
    get_processed_invoices_form = GetProcessedInvoicesForm()
    if not get_processed_invoices_form.validate():
        abort(400)
    user_invoice_matches = user_invoice_match_model.get_invoice_matches(
        current_user.sub,
        get_processed_invoices_form.offset,
        get_processed_invoices_form.per_page,
    )
    return jsonify(
        matches=list(map(_user_invoice_match_to_output_dict, user_invoice_matches))
    )
