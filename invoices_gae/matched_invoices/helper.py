#coding: utf-8

def readable_month(month):
    try:
        month_i = int(month)
    except (TypeError, ValueError):
        return None
    return "{} ~ {}".format(month_i * 2 - 1, month_i * 2)
