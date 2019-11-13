from scrapy.crawler import CrawlerProcess
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoices.crawler import context
from invoices.crawler.prize import PrizeSpider
from invoices.model import PrizeModel

crawler_settings = {
    "ITEM_PIPELINES": {
        "invoices.crawler.prize.SpawnSubPrizesPipeline": 100,
        "invoices.crawler.model_pipeline.SavePrizePipeline": 200,
    }
}


def run_fetch_prizes_job(config):
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    context.prize_model = PrizeModel(session)

    cp = CrawlerProcess(crawler_settings)
    cp.crawl(PrizeSpider)
    cp.start()

    session.commit()
