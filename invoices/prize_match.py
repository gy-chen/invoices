def is_date_match(prize_year, prize_month, invoice_year, invoice_month):
    return prize_year == invoice_year and prize_month == invoice_month

def is_number_match(prize_number, invoice_number):
    return invoice_number.endswith(prize_number)