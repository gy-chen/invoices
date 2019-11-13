import enum
import re
import scrapy
from invoices.common import PrizeType, Month


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
        "01-02": Month.MONTH_1_2,
        "03-04": Month.MONTH_3_4,
        "05-06": Month.MONTH_5_6,
        "07-08": Month.MONTH_7_8,
        "09-10": Month.MONTH_9_10,
        "11-12": Month.MONTH_11_12,
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
            PrizeType.SPECIAL_TOP_AWARD,
            PrizeType.TOP_AWARD,
            PrizeType.FIRST_AWARD,
            PrizeType.FIRST_AWARD,
            PrizeType.FIRST_AWARD,
        ]
        for number, type in zip(normals, normal_types):
            yield PrizeItem(year=year, month=month_range, type=type, number=number)

    def _parse_year(self, raw):
        return int(raw)

    def _parse_month_range(self, raw):
        return self._RAW_MONTH_RANGE_MAPPING[raw]


class SpawnSubPrizesPipeline:
    def process_item(self, item, spider):
        type = item.get("type")
        if type != PrizeType.FIRST_AWARD:
            return item
        subprizes = self._spawn(item)
        self._add_items_to_pipeline(subprizes, spider)
        return item

    def _spawn(self, prize):
        types = [
            PrizeType.SECOND_AWARD,
            PrizeType.THIRD_AWARD,
            PrizeType.FOURTH_AWARD,
            PrizeType.FIFTH_AWARD,
            PrizeType.SIXTH_AWARD,
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