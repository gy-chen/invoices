import collections

Prize = collections.namedtuple("Prize", "type year month number prize")


class PrizeModel:
    def add_prize(self, type, year, month, number, prize):
        return NotImplemented

    def delete_prize(self, type_, year, month, number):
        return NotImplemented

    def get_prizes(self):
        return NotImplemented


def is_match(prize, invoice):
    """Is invoice matches the prize

    Args:
        prize (invoices.prize.model.Prize)
        invoice (invoices.prize.model.Invoice)

    Returns:
        True if matched, otherwise False
    """
    prize_year = prize.year
    prize_month = prize.month
    prize_number = prize.number

    invoice_year = invoice.year
    invoice_month = invoice.month
    invoice_number = invoice.number

    return is_date_match(
        prize_year, prize_month, invoice_year, invoice_month
    ) and is_number_match(prize_number, invoice_number)


def is_date_match(prize_year, prize_month, invoice_year, invoice_month):
    return prize_year == invoice_year and prize_month == invoice_month


def is_number_match(prize_number, invoice_number):
    return invoice_number.endswith(prize_number)
