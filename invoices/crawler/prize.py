import enum
import re
import scrapy


class PrizeTypeEnum(enum.Enum):
    SPECIAL_TOP_AWARD = 1
    TOP_AWARD = 2
    FIRST_AWARD = 3
    SECOND_AWARD = 4
    THIRD_AWARD = 5
    FOURTH_AWARD = 6
    FIFTH_AWARD = 7
    SIXTH_AWARD = 8
    SPECIAL_SIXTH_AWARD = 9


class PrizeMonthEnum(enum.Enum):
    MONTH_1_2 = 1
    MONTH_3_4 = 2
    MONTH_5_6 = 3
    MONTH_7_8 = 4
    MONTH_9_10 = 5
    MONTH_11_12 = 6


class PrizeItem(scrapy.Item):
    year = scrapy.Field()
    month = scrapy.Field()
    type = scrapy.Field()
    number = scrapy.Field()


class PrizeSpider(scrapy.Spider):
    name = "prizespider"
    start_urls = ["http://invoice.etax.nat.gov.tw/"]

    _PAT_DATE = re.compile(r"\W(\d{3})年\d({2}-\d{2})月\W")
    _PAT_NORMAL_PRIZES = re.compile(r"\b\d{8}\b")
    _PAT_SIXTH_PRIZES = re.compile(r"\b\d{3}\b")

    def parse(self, response):
        year, month_range = response.css("#area1").re(self._PAT_DATE)

        normals = response.css("#area1 table").re(self._PAT_NORMAL_PRIZES)
        if len(normals) != 5:
            raise ValueError("unexpect invoice page format")
        normal_types = [
            PrizeTypeEnum.SPECIAL_TOP_AWARD,
            PrizeTypeEnum.TOP_AWARD,
            PrizeTypeEnum.FIRST_AWARD,
            PrizeTypeEnum.FIRST_AWARD,
            PrizeTypeEnum.FIRST_AWARD,
        ]
        for number, type in zip(normals, normal_types):
            yield PrizeItem()

