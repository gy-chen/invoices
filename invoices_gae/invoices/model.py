#coding: utf-8
import six
from flask import current_app
from google.cloud import datastore
from ..auth import get_auth_manager_instance
from ..common import validator

# use app.request_with_context to test this function
def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])


class InvoiceColumn:
    YEAR = 'year'
    MONTH = 'month'
    NUMBER = 'number'
    NOTE = 'note'
    # save the id of the prize model here
    MATCHED_PRIZE_ID = 'matched_prize_id'
    USER_ID = 'user_id'


class Invoice:
    """Invoice that stored in Google datastore

    """
    KEY = 'Invoice'

    DEFAULT_ORDER = [
        '-' + InvoiceColumn.YEAR,
        '-' + InvoiceColumn.MONTH,
        InvoiceColumn.NUMBER]

    @classmethod
    def update(cls, data, id):
        ds = get_client()
        if id:
            key = ds.key(cls.KEY, int(id))
        else:
            key = ds.key(cls.KEY)

        entity = datastore.Entity(
            key=key,
            exclude_from_indexes=[InvoiceColumn.NOTE])
        entity.update(data)
        ds.put(entity)
        return entity

    @classmethod
    def create(cls, data):
        return cls.update(data, None)

    @classmethod
    def list(cls, limit=10, cursor=None, filters=[], order=DEFAULT_ORDER):
        ds = get_client()

        query = ds.query(
            kind=cls.KEY,
            order=order)
        for filter_ in filters:
            query.add_filter(*filter_)
        query_iterator = query.fetch(limit=limit, start_cursor=cursor)
        page = next(query_iterator.pages)

        next_cursor = (
            query_iterator.next_page_token.decode('utf-8')
            if page.remaining == limit else None)
        entities = list(page)

        return entities, next_cursor

    @classmethod
    def list_of_user(cls, user_id, limit=10, cursor=None):
        """List the invoices of the user
        """
        filters = [
            (InvoiceColumn.USER_ID, '=', user_id)
        ]
        return cls.list(limit, cursor, filters)

    @classmethod
    def list_unmatched(cls, user_id=None, limit=None, cursor=None):
        filters = []
        if user_id:
            filters.append((InvoiceColumn.USER_ID, '=', user_id))
        filters.append((InvoiceColumn.MATCHED_PRIZE_ID, '=', None))
        return cls.list(limit, cursor, filters)

    @classmethod
    def list_matched(cls, user_id=None, limit=10, cursor=None):
        filters = []
        if user_id:
            filters.append((InvoiceColumn.USER_ID, '=', user_id))
        filters.append((InvoiceColumn.MATCHED_PRIZE_ID, '>', 0))
        order = [InvoiceColumn.MATCHED_PRIZE_ID] + cls.DEFAULT_ORDER
        return cls.list(limit, cursor, filters, order)

    @classmethod
    def read(cls, id):
        ds = get_client()
        key = ds.key(cls.KEY, int(id))
        entity = ds.get(key)
        return entity

    @classmethod
    def delete(cls, id):
        ds = get_client()
        key = ds.key(cls.KEY, int(id))
        ds.delete(key)

    @classmethod
    def is_invoice_exists(cls, year, month, number, exclude_id=None):
        ds = get_client()
        query = ds.query(kind=cls.KEY)
        query.add_filter(InvoiceColumn.NUMBER, '=', number)
        query.add_filter(InvoiceColumn.YEAR, '=', year)
        query.add_filter(InvoiceColumn.MONTH, '=', month)
        iterator = query.fetch()
        page = next(iterator.pages)
        if not exclude_id:
            return bool(next(page, False))
        matched_invoice = next(page, False)
        if not matched_invoice:
            return False
        return matched_invoice.key != ds.key(cls.KEY, int(exclude_id))


class InvoiceModel:
    """Contains business logic for invoice

    """

    @classmethod
    def for_add(cls, data):
        """Apply invoice add logic

        This method will fetch id of the login user and associate it to the
        invoice.

        return data dict that can be used in invoice creation.
        """
        if InvoiceColumn.USER_ID not in data:
            data[InvoiceColumn.USER_ID] = cls.get_login_user_id()
        InvoiceSanitizer.for_add(data)
        validate_errors = InvoiceValidator.for_add(data)
        if validate_errors:
            raise InvalidInvoiceException(*validate_errors)
        # check duplicated invoices
        if Invoice.is_invoice_exists(data[InvoiceColumn.YEAR],
                                     data[InvoiceColumn.MONTH],
                                     data[InvoiceColumn.NUMBER]):
            raise InvalidInvoiceException("The invoice is duplicated.")
        return data

    @classmethod
    def for_update(cls, data, id):
        """Apply invoice update logic

        return data dict that can be used in invoice updating.
        """
        InvoiceSanitizer.for_update(data)
        validate_errors = InvoiceValidator.for_update(data)
        if validate_errors:
            raise InvalidInvoiceException(*validate_errors)
        # check duplicated invoices
        if Invoice.is_invoice_exists(data[InvoiceColumn.YEAR],
                                     data[InvoiceColumn.MONTH],
                                     data[InvoiceColumn.NUMBER],
                                     id):
            raise InvalidInvoiceException("The invoice is duplicated.")
        return data

    @classmethod
    def get_login_user_id(cls):
        auth_manager = get_auth_manager_instance()
        return auth_manager.get_login_user()['id']


class InvoiceApiModel(InvoiceModel):

    _login_user = {}

    @classmethod
    def validate_login_jwt(cls, jwt):
        auth_manager = get_auth_manager_instance()
        login_user = auth_manager.get_login_user_by_jwt(jwt)
        cls._login_user = login_user
        return login_user.get('id', None)

    @classmethod
    def get_login_user_id(cls):
        return cls._login_user.get('id', None)


class InvoiceValidator:
    """Validator for Invoice

    Use this validator to ensure invoice having columns
    appropriate for actions defined in app.
    """

    @classmethod
    def for_add(cls, data):
        """Check data for add action

        Ensure data that have all the columns that needed
        for add action.

        return:
          (...InvalidInvoiceException): return list of InvalidInvoiceException
          if any invalid values occurs.
        """
        result = []
        validators = [
            cls.check_year,
            cls.check_month,
            cls.check_number,
            cls.check_note,
            cls.check_matched_prize_id
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
        """檢查發票年份

        使用民國年，限定阿拉伯數字輸入
        如果年份錯誤·則InvalidInvoiceException
        """
        if InvoiceColumn.YEAR not in data:
            raise InvalidYearException('Please input year')
        validator.check_year(data[InvoiceColumn.YEAR])

    @classmethod
    def check_month(cls, data):
        """檢查月份

        1 -> 1 ~ 2月
        2 -> 3 ~ 4月
        3 -> 5 ~ 6月
        4 -> 7 ~ 8月
        5 -> 9 ~ 10月
        6 -> 11 ~ 12月

        如果月份錯誤，則丟出InvalidInvoiceException
        """
        if InvoiceColumn.MONTH not in data:
            raise InvalidMonthException('Plase input month')
        validator.check_month(data[InvoiceColumn.MONTH])

    @classmethod
    def check_number(cls, data):
        """Check invoice number

        number must be digits and length must be 8.
        raise InvalidInvoiceException if not meet these.
        """
        if InvoiceColumn.NUMBER not in data:
            raise InvalidNumberException('Plase input number')
        number = six.text_type(data[InvoiceColumn.NUMBER])
        if not number.isdigit() or len(number) != 8:
            raise InvalidNumberException('Number is not valid')

    @classmethod
    def check_note(cls, data):
        pass

    @classmethod
    def check_user_id(cls, data):
        if InvoiceColumn.USER_ID not in data:
            raise InvalidUserIdException('Please input user id')

    @classmethod
    def check_matched_prize_id(cls, data):
        if InvoiceColumn.MATCHED_PRIZE_ID not in data:
            return InvalidMatchedPrizeIdException('Please input id of the matched prize')


class InvoiceSanitizer:
    """Sanitize data of invoice

    """

    @classmethod
    def for_add(cls, data):
        cls.sanitize_year(data)
        cls.sanitize_month(data)
        cls.sanitize_number(data)
        cls.sanitize_note(data)
        cls.sanitize_user_id(data)
        cls.sanitize_matched_prize_id(data)

    @classmethod
    def for_update(cls, data):
        cls.for_add(data)

    @classmethod
    def sanitize_year(cls, data):
        cls._sanitize(data, InvoiceColumn.YEAR, lambda x: six.text_type(x).strip())

    @classmethod
    def sanitize_month(cls, data):
        cls._sanitize(data, InvoiceColumn.MONTH, lambda x: int(x))

    @classmethod
    def sanitize_number(cls, data):
        cls._sanitize(data, InvoiceColumn.NUMBER, lambda x: six.text_type(x).strip())

    @classmethod
    def sanitize_note(cls, data):
        cls._sanitize(data, InvoiceColumn.NOTE, lambda x: six.text_type(x).strip())

    @classmethod
    def sanitize_user_id(cls, data):
        cls._sanitize(data, InvoiceColumn.USER_ID, lambda x: six.text_type(x).strip())

    @classmethod
    def sanitize_matched_prize_id(cls, data):
        cls._sanitize(data, InvoiceColumn.MATCHED_PRIZE_ID, lambda x: int(x))

    @staticmethod
    def _sanitize(data, column_name, sanitize_function):
        try:
            column = data[column_name]
            sanitized_column = sanitize_function(column)
        except (ValueError, TypeError, KeyError):
            sanitized_column = None
        data[column_name] = sanitized_column


class InvalidInvoiceException(Exception): pass
class InvalidYearException(InvalidInvoiceException): pass
class InvalidMonthException(InvalidInvoiceException): pass
class InvalidNumberException(InvalidInvoiceException): pass
class InvalidNoteException(InvalidInvoiceException): pass
class InvalidUserIdException(InvalidInvoiceException): pass
class InvalidMatchedPrizeIdException(InvalidInvoiceException): pass
