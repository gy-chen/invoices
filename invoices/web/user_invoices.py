from flask import Blueprint, abort, jsonify, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length
from werkzeug.datastructures import MultiDict
from invoices.web.login import required_login, current_user
from invoices.web import db, invoice_model, user_invoice_model
from invoices.model import Invoice, InvoiceMonthEnum

bp = Blueprint("user_invoices", __name__)


def _month_to_enum(month):
    month_map = {
        1: InvoiceMonthEnum.MONTH_1_2,
        2: InvoiceMonthEnum.MONTH_3_4,
        3: InvoiceMonthEnum.MONTH_5_6,
        4: InvoiceMonthEnum.MONTH_7_8,
        5: InvoiceMonthEnum.MONTH_9_10,
        6: InvoiceMonthEnum.MONTH_11_12,
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
        invoice = add_invoice_form.to_invoice()
        saved_invoice = invoice_model.add_invoice(*invoice.to_add_invoice_args())
        db.commit()
        user_invoice_model.add_user_invoice(saved_invoice.id, current_user.sub)
        db.commit()
        return jsonify(invoice_id=saved_invoice.id)
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
        db.commit()
        return ("", 204)
    abort(400)


@bp.route("/invoice/<int:id>", methods=["DELETE"])
@required_login
def delete_invoice(id):
    try:
        invoice_model.delete_invoice(id)
    except ValueError:
        abort(400)
    db.commit()
    return ("", 204)


@bp.route("/invoices", methods=["GET"])
@required_login
def get_invoices():
    pass


@bp.route("/invoices/processed")
@required_login
def get_processed_invoices():
    pass
