#coding: utf-8
import logging
import six
from flask import current_app
from google.cloud import datastore
from ..common import validator
from .crawler import prizesgetter, prizesparser

def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])

class PrizeColumn:
    YEAR = 'year'
    MONTH = 'month'
    TYPE = 'type'
    NUMBER = 'number'


class Prize:
    """Prize that stored in Google datastore

    """
    KEY = 'Prize'

    @classmethod
    def update(cls, data, id):
        ds = get_client()
        if id:
            key = ds.key(cls.KEY, int(id))
        else:
            key = ds.key(cls.KEY)

        entity = datastore.Entity(
            key=key,
            exclude_from_indexes=[PrizeColumn.NUMBER]
        )
        entity.update(data)
        ds.put(entity)
        return entity

    @classmethod
    def create(cls, data):
        return cls.update(data, None)

    @classmethod
    def list(cls, limit=10, cursor=None):
        ds = get_client()

        query = ds.query(
            kind=cls.KEY,
            order=[
                '-' + PrizeColumn.YEAR,
                '-' + PrizeColumn.MONTH,
                PrizeColumn.TYPE
            ])
        query_iterator = query.fetch(limit=limit, start_cursor=cursor)
        page = next(query_iterator.pages)

        next_cursor = (
            query_iterator.next_page_token.decode('utf-8')
            if page.remaining == limit else None)
        entities = list(page)

        return entities, next_cursor

    @classmethod
    def auth_fetch_prizes(cls):
        """Prizes Auto Fetcher

        Auto fetch current, previous prizes information and save these to Pirzes model
        """
        # fetch current and previous prizes
        pg = prizesgetter.PrizesGetter()
        prizes_html = pg.get_page_content()
        logging.debug(type(prizes_html))
        pp = prizesparser.PrizesParser(prizes_html)
        # check the prizes are exists or not.
        if not cls._is_prizes_exists(
            pp.get_current_prizes_year(),
            pp.get_current_prizes_month()):
            # save current prizes
            cls._save_auto_fetched_prizes(
                pp.get_current_prizes_year(),
                pp.get_current_prizes_month(),
                pp.get_current_prizes())
        if not cls._is_prizes_exists(
            pp.get_previous_prizes_year(),
            pp.get_previous_prizes_month()):
            # save previous prizes
            cls._save_auto_fetched_prizes(
                pp.get_previous_prizes_year(),
                pp.get_previous_prizes_month(),
                pp.get_previous_prizes())

    @classmethod
    def match_prize(cls, year, month, number):
        """Try to find a match prize of the specific year, month and number

        This method will try to match the biggest prizes stored in the model.

        raise UnpublicPrizeException if the prizes is not published.

        () -> return Prize if mathched else None
        """
        ds = get_client()
        query = ds.query(kind=cls.KEY)
        query.add_filter(PrizeColumn.YEAR, '=', year)
        query.add_filter(PrizeColumn.MONTH, '=', month)
        number_s = six.text_type(number)
        prizes = list(query.fetch())
        print (year, month, prizes)
        if not prizes:
            raise UnpublicPrizeException()
        matched_prizes = [prize for prize in prizes if number_s.endswith(prize[PrizeColumn.NUMBER])]
        # try to return the biggest matched prize
        return min(matched_prizes, key=lambda p: p[PrizeColumn.TYPE]) if matched_prizes else None

    @classmethod
    def _save_auto_fetched_prizes(cls, year, month, prizes):
        """Save fetched prizes to the model

        year: year of the prizes
        month: month of the prizes
        prizes: list of Prize (object type from crawler prizesparser module)
        """
        for prize in prizes:
            data = {
                PrizeColumn.YEAR: year,
                PrizeColumn.MONTH: month,
                PrizeColumn.TYPE: prize.get_type(),
                PrizeColumn.NUMBER: prize.get_number()
            }
            PrizeSanitizer.for_add(data)
            cls.create(data)

    @classmethod
    def _is_prizes_exists(cls, year, month):
        """Check whether the prizes of specific date exists.

        (year, month) -> bool
        """
        year_s = six.text_type(year)
        month_i = int(month)
        ds = get_client()
        query = ds.query(kind=cls.KEY)
        query.add_filter(PrizeColumn.YEAR, '=', year_s)
        query.add_filter(PrizeColumn.MONTH, '=', month_i)
        iterator = query.fetch()
        page = next(iterator.pages)
        return bool(next(page, False))


class PrizeValidator:
    """Validator for Prize

    """

    @classmethod
    def for_add(cls, data):
        """Check data for add action

        Ensure data that have all the columns that needed
        for add action.

        return:
          (...InvalidPrizeException): return list of InvalidPrizeException
          if any invalid values occurs.
        """
        result = []
        validators = [
            cls.check_year,
            cls.check_month,
            cls.check_number,
            cls.check_type
        ]
        for validator in validators:
            try:
                validator(data)
            except InvalidInvoiceException as e:
                result.append(e)
        return result

    @classmethod
    def for_update(cls, data):
        return cls.for_add(data)

    @classmethod
    def check_year(cls, data):
        if PrizeColumn.YEAR not in data:
            raise InvalidYearException('Plase input year')
        validator.check_year(data[PrizeColumn.YEAR], InvalidYearException)

    @classmethod
    def check_month(cls, data):
        if PrizeColumn.MONTH not in data:
            raise InvalidMonthException('Plase input month')
        validator.check_month(data[PrizeColumn.MONTH], InvalidMonthException)

    @classmethod
    def check_type(cls, data):
        """Check prize's type

        1 => 特別獎
        2 => 特獎
        3 => 頭獎
        4 => 二獎
        5 => 三獎
        6 => 四獎
        7 => 五獎
        8 => 六獎
        9 => 增開六獎

        otherwise, raise InvalidTermException
        """
        if PrizeColumn.TYPE not in data:
            raise InvalidTermException('Please input type')
        type = data[PrizeColumn.TYPE]
        try:
            type_i = int(type)
            if type_i < 1 or type_i > 9:
                raise ValueError
        except (ValueError, TypeError):
            raise InvalidTermException('Please input type between 1 ~ 9')

    @classmethod
    def check_number(cls, data):
        """Check prize's number

        Prize's number length must be between 3 ~ 8,
        otherwise, raise InvalidNumberException
        """
        if PrizeColumn.NUMBER not in data:
            raise InvalidNumberException('Please input number')
        number = data[PrizeColumn.NUMBER]
        number_s = six.text_type(number)
        if (not number_s.is_digit() or
            len(number_s) < 3 or
            len(number_s) > 8):
            raise InvalidNumberException("Prize's number length must betwen 3 to 8")


class PrizeSanitizer:
    """PrizeSanitizer

    Provide sanitize functions to Prize columns.
    """

    @classmethod
    def for_add(cls, data):
        cls.sanitize_year(data)
        cls.sanitize_month(data)
        cls.sanitize_number(data)
        cls.sanitize_type(data)

    @classmethod
    def for_update(cls, data):
        cls.for_add(data)

    @classmethod
    def sanitize_year(cls, data):
        cls._sanitize(data, PrizeColumn.YEAR, lambda year: six.text_type(year).strip())

    @classmethod
    def sanitize_month(cls, data):
        cls._sanitize(data, PrizeColumn.MONTH, lambda month: int(month))

    @classmethod
    def sanitize_number(cls, data):
        cls._sanitize(data, PrizeColumn.NUMBER, lambda number: six.text_type(number).strip())

    @classmethod
    def sanitize_type(cls, data):
        cls._sanitize(data, PrizeColumn.TYPE, lambda type_: int(type_))

    @staticmethod
    def _sanitize(data, column_name, sanitize_function):
        try:
            column = data[column_name]
            sanitized_column = sanitize_function(column)
        except (ValueError, TypeError, KeyError):
            sanitized_column = None
        data[column_name] = sanitized_column


class InvalidPrizeException(Exception): pass
class InvalidYearException(InvalidPrizeException): pass
class InvalidMonthException(InvalidPrizeException): pass
class InvalidNumberException(InvalidPrizeException): pass
class InvalidTermException(InvalidPrizeException): pass

class UnpublicPrizeException(Exception): pass
