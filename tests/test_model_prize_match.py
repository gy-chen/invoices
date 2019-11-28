from invoices.common import Month
from invoices.prize.model import Prize
from invoices.invoice.model import Invoice
from invoices.prize.model import is_match


def test_is_match():
    prize1 = Prize(None, 108, Month.MONTH_7_8, "45698621", None)
    prize2 = Prize(None, 108, Month.MONTH_7_8, "621", None)
    invoice1 = Invoice(None, 108, Month.MONTH_7_8, "45698621", None)
    invoice2 = Invoice(None, 109, Month.MONTH_7_8, "45698621", None)
    invoice3 = Invoice(None, 108, Month.MONTH_5_6, "45698621", None)
    invoice4 = Invoice(None, 108, Month.MONTH_7_8, "46698621", None)

    assert is_match(prize1, invoice1)
    assert not is_match(prize1, invoice2)
    assert not is_match(prize1, invoice3)
    assert not is_match(prize1, invoice4)

    assert is_match(prize2, invoice1)
    assert not is_match(prize2, invoice2)
    assert not is_match(prize2, invoice3)
    assert is_match(prize2, invoice4)
