from scrapy.crawler import CrawlerProcess
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from crawler_setting import PrizeCrawlerSetting as setting
from invoices.crawler import context
from invoices.crawler.prize import PrizeSpider
from invoices.model import PrizeModel

engine = create_engine(setting['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
session = Session()
context.prize_model = PrizeModel(session)

cp = CrawlerProcess(setting)
cp.crawl(PrizeSpider)
cp.start()

session.commit()