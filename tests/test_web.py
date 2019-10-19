from werkzeug.datastructures import MultiDict
from invoices.web.user_invoices import AddInvoiceForm
from invoices.web.user_invoices import UpdateInvoiceForm
from invoices.model import InvoiceMonthEnum


def test_add_invoice_form(app):
    normal_data = MultiDict(
        {"year": "108", "month": "1", "number": "12345678", "note": "note"}
    )
    normal_add_invoice_form = AddInvoiceForm(normal_data)
    assert normal_add_invoice_form.validate()

    assert normal_add_invoice_form.to_add_invoice_args() == (
        108,
        InvoiceMonthEnum.MONTH_1_2,
        "12345678",
        "note",
    )

    invalid_year_data = MultiDict(
        {"year": "2019", "month": "1", "number": "12345678", "note": "note"}
    )
    invalid_year_add_invoice_form = AddInvoiceForm(invalid_year_data)
    assert not invalid_year_add_invoice_form.validate()

    invalid_month_data_1 = MultiDict(
        {"year": "108", "month": "0", "number": "12345678", "note": "note"}
    )
    invalid_month_add_invoice_form_1 = AddInvoiceForm(invalid_month_data_1)
    assert not invalid_month_add_invoice_form_1.validate()

    invalid_month_data_2 = MultiDict(
        {"year": "108", "month": "7", "number": "12345678", "note": "note"}
    )
    invalid_month_add_invoice_form_2 = AddInvoiceForm(invalid_month_data_2)
    assert not invalid_month_add_invoice_form_2.validate()

    invalid_number_data = MultiDict(
        {"year": "108", "month": "1", "number": "1234567", "note": "note"}
    )
    invalid_number_add_invoice_form = AddInvoiceForm(invalid_number_data)
    assert not invalid_number_add_invoice_form.validate()


def test_update_invoice_form(app):
    normal_data = MultiDict(
        {"id": "1", "year": "108", "month": "1", "number": "12345678", "note": "note"}
    )
    normal_update_form = UpdateInvoiceForm(normal_data)
    assert normal_update_form.validate()

    assert normal_update_form.to_update_invoice() == (
        1,
        108,
        InvoiceMonthEnum.MONTH_1_2,
        "12345678",
        "note",
    )
