#!/usr/bin/env python3
import re
from bs4 import BeautifulSoup


class PrizesParser:
    """ parse the prizes information page.
    """
    # search for year and months of the prizes page
    _pattern_date = re.compile(r'(\d{3})年(\d{2})-(\d{2})月')
    # pattern for searching prize numbers of the prizes page
    _pattern_prizes = re.compile('(\\d{8}).*?(\\d{8}).*?(\\d{8})、(\\d{8})、(\\d{8}).*?(\\d{3})、(\\d{3})、(\\d{3})', re.DOTALL)

    def __init__(self, page_content):
        self._soup = BeautifulSoup(page_content, 'html.parser')
        # the div of current prizes information
        find_area1 = self._soup.find_all(attrs={'id': 'area1'})
        if len(find_area1) < 1:
            raise RuntimeError('Cannot find current prizes information. (is <div id="area1"> in the page content?)')
        self._area1 = find_area1[0]
        # the div of previous prizes information
        find_area2 = self._soup.find_all(attrs={'id': 'area2'})
        if len(find_area2) < 1:
            raise RuntimeError('Cannot find current prizes information. (is <div id="area2"> in the page content?)')
        self._area2 = find_area2[0]

    def get_current_prizes_year(self):
        """get year number of current prizes

        () -> int
        """
        match = self._get_date_match(self._area1.text)
        return int(match.groups()[0])

    def get_current_prizes_month(self):
        """get month of current prizes

        return 1 if 1~2 month
               2 if 3~4 month
               3 if 5~6 month
               4 if 7~8 month
               5 if 9~10 month
               6 if 11~12 month
        () -> int
        """
        match = self._get_date_match(self._area1.text)
        return int(match.groups()[2]) // 2

    def get_current_prizes(self):
        """Get a list of current prizes

        raise RuntimeError if cannot find the prize numbers in 
        the page content.
        () -> list of Prize type instances
        """
        return self._parse_numbers(self._area1.text)

    def get_previous_prizes(self):
        """Get a list of previous prizes

        raise RuntimeError if cannot find the prize numbers in
        the page content.
        () -> list of Prize type instances
        """
        return self._parse_numbers(self._area2.text)

    def get_previous_prizes_year(self):
        match = self._get_date_match(self._area2.text)
        # TODO avoid duplicated logic in method get_current_prizes_year
        return int(match.groups()[0])

    def get_previous_prizes_month(self):
        match = self._get_date_match(self._area2.text)
        # TODO avoid duplicated logic in method get_current_prizes_month
        return int(match.groups()[2]) // 2

    def _get_date_match(self, text):
        """try to match date on given text

        raise RuntimeError if no match found.
        () -> SRE_Match
        """
        match = self._pattern_date.search(text)
        if not match:
            raise RuntimeError('Cannot find year in the page content. (Comes Taiwan year xxxx?)')
        return match

    def _parse_numbers(self, text):
        match = self._pattern_prizes.search(text)
        if not match:
            raise RuntimeError('Cannot find numbers in the page content.')
        numbers = match.groups()
        prizes = []
        number_jackpot = numbers[0]
        prizes.append(Prize(Prize.TYPE_JACKPOT, number_jackpot))
        number_special = numbers[1]
        prizes.append(Prize(Prize.TYPE_SPECIAL, number_special))
        numbers_first = numbers[2:5]
        for number_first in numbers_first:
            # First prize will spawn other prizes
            prizes.append(Prize(Prize.TYPE_FIRST, number_first))
            number_second = number_first[1:]
            prizes.append(Prize(Prize.TYPE_SECOND, number_second))
            number_third = number_first[2:]
            prizes.append(Prize(Prize.TYPE_THIRD, number_third))
            number_fourth = number_first[3:]
            prizes.append(Prize(Prize.TYPE_FOURTH, number_fourth))
            number_fifth = number_first[4:]
            prizes.append(Prize(Prize.TYPE_FIFTH, number_fifth))
            number_sixth = number_first[5:]
            prizes.append(Prize(Prize.TYPE_SIXTH, number_sixth))
        numbers_encore_sixth = numbers[5:]
        prizes.extend([Prize(Prize.TYPE_ENCORE_SIXTH, number_encore_sixth) for number_encore_sixth in numbers_encore_sixth])
        return prizes

class Prize:
    """ Represent a prize.
    """
    TYPE_JACKPOT = 1
    TYPE_SPECIAL = 2
    TYPE_FIRST = 3
    TYPE_SECOND = 4
    TYPE_THIRD = 5
    TYPE_FOURTH = 6
    TYPE_FIFTH = 7
    TYPE_SIXTH = 8
    TYPE_ENCORE_SIXTH = 9
    
    _TYPE_NAME_MAPPINGS = {
        1: '特別獎',
        2: '特獎',
        3: '頭獎',
        4: '二獎',
        5: '三獎',
        6: '四獎',
        7: '五獎',
        8: '六獎',
        9: '增開六獎'
        }

    _TYPE_PRIZE_MAPPINGS = {
        1: 10000000, # 1000 W
        2: 2000000, # 200 W
        3: 200000, # 20 W
        4: 40000, # 4W
        5: 10000, # 1W
        6: 4000, # 4K
        7: 1000, # 1K
        8: 200,
        9: 200
        }

    def __init__(self, type_, number):
        """init

        For acceptable type_ values, see constants of this class.
        raise ValueError if type_ if not acceptable.
        """
        type_ = int(type_)
        if type_ < 1 or type_ > 9:
            raise ValueError('Not acceptable type_ value')
        self._type = type_
        self._number = number

    def get_type(self):
        """Get the type of this prize

        () -> int
        """
        return self._type

    def get_type_name(self):
        """Get the type name of this prize

        () -> str
        """
        return self._TYPE_NAME_MAPPINGS[self._type]

    def get_prize(self):
        """Get the prize of this prize

        () -> int
        """
        return self._TYPE_PRIZE_MAPPINGS[self._type]

    def get_number(self):
        """Get the number of this prize

        () -> str
        """
        return self._number

    def __repr__(self):
        return '{0}({1}, {2})'.format(
            self.__class__.__name__,
            self._type,
            self._number
            )

if __name__ == '__main__':
    with open('prizes.html', 'r') as f:
        demo_content = f.read()
    parser = PrizesParser(demo_content)
    print('-start to extract current prizes information-')
    print('year:', parser.get_current_prizes_year())
    print('month:', parser.get_current_prizes_month())
    print('prizes:', ', \n\t'.join([prize.__repr__() for prize in parser.get_current_prizes()]))
    print('-start to extract previous prizes information-')
    print('year:', parser.get_previous_prizes_year())
    print('month:', parser.get_previous_prizes_month())
    print('prizes:', ', \n\t'.join([prize.__repr__() for prize in parser.get_previous_prizes()]))
