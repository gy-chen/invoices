from invoices.model import InvoiceModel, Invoice, InvoiceMonthEnum
from invoices.model import PrizeModel, Prize, PrizeMonthEnum, PrizeTypeEnum
from invoices.model import InvoiceMatchModel, InvoiceMatch
from invoices.model import UserModel, User
from invoices.model import UserInvoiceModel, UserInvoice
from invoices.model import UserInvoiceMatchModel, UserInvoiceMatch


def test_invoice_crud(session):
    invoice_model = InvoiceModel(session)

    invoice = Invoice(None, 108, InvoiceMonthEnum.MONTH_9_10, "12345678", "note")

    invoice_model.add_invoice(*invoice[1:])
    session.commit()
    assert invoice_model.get_last_added_invoice_id() is not None

    saved_invoice = invoice_model.get_invoices()[0]
    assert tuple(saved_invoice)[1:] == invoice[1:]

    update_invoice = Invoice(
        saved_invoice.id, 107, InvoiceMonthEnum.MONTH_7_8, "87654321", "updated note"
    )

    invoice_model.update_invoice(update_invoice)
    session.commit()
    saved_invoice = invoice_model.get_invoices()[0]

    assert saved_invoice[:] == update_invoice[:]

    invoice_model.delete_invoice(saved_invoice.id)
    session.commit()

    assert not invoice_model.get_invoices()


def test_prize_crud(session):
    prize_model = PrizeModel(session)

    prize_model.add_prize(
        PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10, "818", 200
    )

    saved_prizes = prize_model.get_prizes()
    assert len(saved_prizes) == 1

    prize = Prize(PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10, "818", 200)
    saved_prize = saved_prizes[0]
    assert saved_prize == prize

    prize_model.delete_prize(PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10)

    assert len(prize_model.get_prizes()) == 0


def test_invoice_match_crud(session):
    invoice_model = InvoiceModel(session)
    prize_model = PrizeModel(session)
    invoice_match_model = InvoiceMatchModel(session)

    invoice_model.add_invoice(108, InvoiceMonthEnum.MONTH_9_10, "12345678", "note")
    prize_model.add_prize(
        PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10, "818", 200
    )
    session.commit()

    saved_invoice = invoice_model.get_invoices()[0]
    saved_prize = prize_model.get_prizes()[0]

    invoice_match = InvoiceMatch(saved_invoice, saved_prize, True)
    invoice_match_model.add_invoice_match(
        saved_invoice.id, saved_prize.type, saved_prize.year, saved_prize.month
    )
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


def test_user_invoice(session):
    invoice_model = InvoiceModel(session)
    user_model = UserModel(session)
    user_invoice_model = UserInvoiceModel(session)

    invoice_model.add_invoice(108, InvoiceMonthEnum.MONTH_9_10, "12345678", "test")
    user = User("testsub", "example@example.org")
    user_model.register_user(user)
    session.commit()

    offset = 0
    per_page = 7
    assert len(user_invoice_model.get_user_invoices(user.sub, offset, per_page)) == 0

    invoice_id = invoice_model.get_last_added_invoice_id()
    user_invoice_model.add_user_invoice(user.sub, invoice_id)

    assert len(user_invoice_model.get_user_invoices(user.sub, offset, per_page)) == 1


def test_user_invoice_match(session):
    invoice_model = InvoiceModel(session)
    user_model = UserModel(session)
    user_invoice_model = UserInvoiceModel(session)
    prize_model = PrizeModel(session)
    invoice_match_model = InvoiceMatchModel(session)
    user_invoice_match_model = UserInvoiceMatchModel(session)

    invoice_model.add_invoice(108, InvoiceMonthEnum.MONTH_9_10, "12345678", "test")
    user = User("testsub", "example@example.org")
    user_model.register_user(user)
    prize_model.add_prize(
        PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10, "818", 200
    )
    session.commit()

    invoice_id = invoice_model.get_last_added_invoice_id()
    user_invoice_model.add_user_invoice(user.sub, invoice_id)
    invoice_match_model.add_invoice_match(
        invoice_id, PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10
    )
    session.commit()

    user_invoice_matches = user_invoice_match_model.get_invoice_matches(user.sub, 0, 7)
    assert len(user_invoice_matches) == 1

    user_invoice_match = user_invoice_matches[0]
    assert user_invoice_match.user == user
    assert user_invoice_match.invoice_match == InvoiceMatch(
        Invoice(invoice_id, 108, InvoiceMonthEnum.MONTH_9_10, "12345678", "test"),
        Prize(PrizeTypeEnum.SIXTH_AWARD, 108, PrizeMonthEnum.MONTH_9_10, "818", 200),
        True,
    )

