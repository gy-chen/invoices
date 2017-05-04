#coding: utf-8

def check_year(year, exception=ValueError):
    """檢查發票年份

    使用民國年，限定阿拉伯數字輸入
    如果年份錯誤·則丟出指定的例外，預設為ValueError
    """
    year = str(year)
    if not year.isdigit():
        raise InvalidYearException('Year is not valid: please input digits.')
    if len(year) >= 4:
        raise InvalidYearException('Year is not valid: plase use Taiwan year.')

def check_month(month, exception=ValueError):
    """檢查月份

    1 -> 1 ~ 2月
    2 -> 3 ~ 4月
    3 -> 5 ~ 6月
    4 -> 7 ~ 8月
    5 -> 9 ~ 10月
    6 -> 11 ~ 12月

    如果月份錯誤，則丟出指定的例外，預設為ValueError
    """
    try:
        month_i = int(month)
    except (ValueError, TypeError):
        raise exception('Month is not valid: please input value between 1 ~ 6')
    if month_i < 1 or month_i > 6:
        raise exception('Month is not valid: please input value between 1 ~ 6')
