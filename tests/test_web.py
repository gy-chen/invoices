from werkzeug.datastructures import MultiDict
from invoices.web.user_invoices import AddInvoiceForm
from invoices.web.user_invoices import UpdateInvoiceForm
from invoices.common import Month


def test_add_invoice_form(app):
    normal_data = MultiDict(
        {"year": "108", "month": "1", "number": "12345678", "note": "note"}
    )
    normal_add_invoice_form = AddInvoiceForm(normal_data)
    assert normal_add_invoice_form.validate()

    assert normal_add_invoice_form.to_add_invoice_args() == (
        108,
        Month.MONTH_1_2,
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
        Month.MONTH_1_2,
        "12345678",
        "note",
    )


def test_invoice_crud(app, logged_in_user, client):
    rv = client.post(
        "/invoice",
        data={"year": "108", "month": "5", "number": "12345678", "note": "test"},
    )
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["invoice_id"] is not None

    update_invoice_data = {
        "year": "109",
        "month": "6",
        "number": "87654321",
        "note": "update_test",
    }
    rv = client.put(f'/invoice/{data["invoice_id"]}', data=update_invoice_data)
    assert rv.status_code == 204

    rv = client.get("/invoices")
    assert rv.status_code == 200
    invoices = rv.get_json()["invoices"]
    assert len(invoices) == 1
    assert invoices[0] == {
        "id": data["invoice_id"],
        "year": 109,
        "month": 6,
        "number": "87654321",
        "note": "update_test",
    }

    rv = client.delete(f'/invoice/{data["invoice_id"]}')
    assert rv.status_code == 204
