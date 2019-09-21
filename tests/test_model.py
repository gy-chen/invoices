from invoices.model import InvoiceModel, Invoice, InvoiceMonthEnum


def test_invoice_crud(session):
    invoiceModel = InvoiceModel(session)

    invoice = Invoice(None, 108, InvoiceMonthEnum.MONTH_9_10, "12345678")

    invoiceModel.add_invoice(invoice)
    session.commit()

    saved_invoice = invoiceModel.get_invoices()[0]

    assert saved_invoice[1:] == invoice[1:]

    update_invoice = Invoice(
        saved_invoice.id, 107, InvoiceMonthEnum.MONTH_7_8, "87654321"
    )

    invoiceModel.update_invoice(update_invoice)
    session.commit()
    saved_invoice = invoiceModel.get_invoices()[0]

    assert saved_invoice[:] == update_invoice[:]

    invoiceModel.delete_invoice(saved_invoice.id)
    session.commit()

    assert not invoiceModel.get_invoices()
