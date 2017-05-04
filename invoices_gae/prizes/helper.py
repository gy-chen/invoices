#coding: utf-8

# use prize type and prize mappings of prizesparser module
from .crawler import prizesparser

def readable_month(month):
    try:
        month_i = int(month)
    except (TypeError, ValueError):
        return None
    return "{} ~ {}".format(month_i * 2 - 1, month_i * 2)

def readable_type(type_):
    try:
        type_i = int(type_)
    except (TypeError, ValueError):
        return None
    return prizesparser.Prize(type_i, '').get_type_name()

def readable_prize(type_):
    try:
        type_i = int(type_)
    except (TypeError, ValueError):
        return None
    return prizesparser.Prize(type_i, '').get_prize()

def prizes_group_by_date(prizes):
    """A filter that return grouped prizes by its year and month.

    prizes: list of prizes data
    return:
      [
        (
            year -> year of the prizes,
            month -> month of the prizes,
            prizes -> ( list of the prizes )
        ),
        ...
      ]
    """
    # key: year, subkey: month
    prizes_group = {}
    for prize in prizes:
        year_prizes_group = prizes_group.get(prize['year'], {})
        month_prizes_group = year_prizes_group.get(prize['month'], [])
        month_prizes_group.append(prize)
        year_prizes_group[prize['month']] = month_prizes_group
        prizes_group[prize['year']] = year_prizes_group
    result = []
    for year, month_groups in prizes_group.items():
        for month, prizes in month_groups.items():
            prizes_t = tuple(prizes)
            result.append((year, month, prizes_t))
    return result
