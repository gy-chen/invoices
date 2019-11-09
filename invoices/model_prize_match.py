from invoices.prize_match import is_date_match, is_number_match


def is_match(prize, invoice):
    """Is invoice matches the prize

    Args:
        prize (invoices.model.Prize)
        invoice (invoices.model.Invoice)

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
