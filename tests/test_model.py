from invoices.model import InvoiceModel, Invoice, InvoiceMonthEnum
from invoices.model import PrizeModel, Prize, PrizeMonthEnum, PrizeTypeEnum
from invoices.model import InvoiceMatchModel, InvoiceMatch
from invoices.model import UserModel, User


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


def test_prize_crud(session):
    prize_model = PrizeModel(session)

    prize = Prize(PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10, "818", 200)

    prize_model.add_prize(prize)

    saved_prizes = prize_model.get_prizes()
    assert len(saved_prizes) == 1

    saved_prize = saved_prizes[0]

    assert saved_prize == prize

    prize_model.delete_prize(PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10)

    assert len(prize_model.get_prizes()) == 0


def test_invoice_match_crud(session):
    invoice_model = InvoiceModel(session)
    prize_model = PrizeModel(session)
    invoice_match_model = InvoiceMatchModel(session)

    invoice_model.add_invoice(
        Invoice(None, 108, InvoiceMonthEnum.MONTH_9_10, "12345678")
    )
    prize_model.add_prize(
        Prize(PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10, "818", 200)
    )
    session.commit()

    saved_invoice = invoice_model.get_invoices()[0]
    saved_prize = prize_model.get_prizes()[0]

    invoice_match = InvoiceMatch(
        saved_invoice.id, saved_prize.type, saved_prize.year, saved_prize.month, False
    )
    invoice_match_model.add_invoice_match(invoice_match)
    session.commit()

    saved_invoice_matches = invoice_match_model.get_invoice_matches()
    assert len(saved_invoice_matches) == 1

    saved_invoice_match = saved_invoice_matches[0]
    assert saved_invoice_match == invoice_match


def test_user(session):
    user_model = UserModel(session)

    user = User("testsub", "example@example.org")

    user_model.register_user(user)

    saved_user = user_model.get_user("testsub")
    assert saved_user == user
