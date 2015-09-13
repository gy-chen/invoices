#!/usr/bin/env python3
import datetime
import urllib.request

# support 'from prizesgetter import *'
__ALL__ = ['PrizesGetter']


class PrizesGetter:
    """Get the page of prizes information for the web.

    The page contains two set of prizes information, and contains
    no previous sets of prizes.
    If current prizes is months 5~6, the page will only contains
    prizes information about months 5~6 and months 3~4. The invoices
    previous months 3~4 have no chances to be matched and can not get
    the prize even the invoice is a matched invoice.
    """
    # source of the prizes information
    _URL = 'http://invoice.etax.nat.gov.tw'
    # datetime format for HTTP Header 'Last-Modified' Data
    _DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

    def __init__(self):
        self._response = None
        self._headers = None

    def get_last_modified_date(self):
        """Get Last modifeid date of the prizes page

        () -> datetime
        """
        if self._headers is not None:
            raw_date = self._headers.get('Last-Modified')
            return datetime.datetime.strptime(raw_date, self._DATE_FORMAT)
        request = urllib.request.Request(self._URL, method='HEAD')
        response = urllib.request.urlopen(request)
        self._headers = response.headers
        return self.get_last_modified_date()

    def get_page_content(self):
        if self._response is not None:
            response = self._response
        else:
            response = urllib.request.urlopen(self._URL)
        page_bytes = response.readall()
        page_content = page_bytes.decode('utf-8')
        return page_content


if __name__ == '__main__':
    getter = PrizesGetter()
    content = getter.get_page_content()
    f = open('prizes.html', 'w')
    f.write(content)
    f.close()
    print('successfully get the prizes page. see prizes.html')
