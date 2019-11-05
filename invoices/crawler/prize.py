import enum
import re
import scrapy
from twisted.internet import defer


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

    _PAT_DATE = re.compile(r"\W(\d{3})年(\d{2}-\d{2})月\W")
    _PAT_NORMAL_PRIZES = re.compile(r"\b\d{8}\b")
    _PAT_SIXTH_PRIZES = re.compile(r"\b\d{3}\b")

    _RAW_MONTH_RANGE_MAPPING = {
        "01-02": PrizeMonthEnum.MONTH_1_2,
        "03-04": PrizeMonthEnum.MONTH_3_4,
        "05-06": PrizeMonthEnum.MONTH_5_6,
        "07-08": PrizeMonthEnum.MONTH_7_8,
        "09-10": PrizeMonthEnum.MONTH_9_10,
        "11-12": PrizeMonthEnum.MONTH_11_12,
    }

    def parse(self, response):
        area1 = response.css("#area1")
        yield from self._parse_area(area1)
        area2 = response.css("#area2")
        yield from self._parse_area(area2)

    def _parse_area(self, selector):
        year_raw, month_range_raw = selector.re(self._PAT_DATE)

        year = self._parse_year(year_raw)
        month_range = self._parse_month_range(month_range_raw)

        normals = selector.re(self._PAT_NORMAL_PRIZES)
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
            yield PrizeItem(year=year, month=month_range, type=type, number=number)

    def _parse_year(self, raw):
        return int(raw)

    def _parse_month_range(self, raw):
        return self._RAW_MONTH_RANGE_MAPPING[raw]


class SpawnSubPrizesPipeline:
    def process_item(self, item, spider):
        print('in pipeline', item)
        type = item.get("type")
        if type != PrizeTypeEnum.FIRST_AWARD:
            return item
        subprizes = self._spawn(item)
        self._add_items_to_pipeline(subprizes, spider)
        return item

    def _spawn(self, prize):
        types = [
            PrizeTypeEnum.SECOND_AWARD,
            PrizeTypeEnum.THIRD_AWARD,
            PrizeTypeEnum.FOURTH_AWARD,
            PrizeTypeEnum.FIFTH_AWARD,
            PrizeTypeEnum.SIXTH_AWARD,
        ]
        number = prize["number"]
        for skip, type in enumerate(types):
            yield PrizeItem(
                type=type,
                year=prize["year"],
                month=prize["month"],
                number=prize["number"][skip:],
            )

    def _add_items_to_pipeline(self, items, spider):
        return spider.crawler.engine.scraper.handle_spider_output(items, None, None, spider)
