#!/usr/bin/env python3
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
    URL = 'http://invoice.etax.nat.gov.tw'

    @classmethod
    def get_page_content(cls):
        response = urllib.request.urlopen(cls.URL)
        page_bytes = response.readall()
        page_content = page_bytes.decode('utf-8')
        return page_content


if __name__ == '__main__':
    content = PrizesGetter.get_page_content()
    f = open('prizes.html', 'w')
    f.write(content)
    f.close()
    print('successfully get the prizes page. see prizes.html')
