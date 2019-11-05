from scrapy.crawler import CrawlerProcess
from crawler_setting import PrizeCrawlerSetting
from invoices.crawler.prize import PrizeSpider

cp = CrawlerProcess(PrizeCrawlerSetting)
cp.crawl(PrizeSpider)
cp.start()