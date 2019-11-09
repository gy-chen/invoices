from scrapy.crawler import CrawlerProcess
from invoices.crawler.prize import PrizeSpider


def test_run_without_error():
    TestCrawlerSetting = {
        "ITEM_PIPELINES": {"invoices.crawler.prize.SpawnSubPrizesPipeline": 100}
    }

    cp = CrawlerProcess(TestCrawlerSetting)
    cp.crawl(PrizeSpider)
    cp.start()
