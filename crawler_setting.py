PrizeCrawlerSetting = {
    'ITEM_PIPELINES': {
        'invoices.crawler.prize.SpawnSubPrizesPipeline': 100,
        'invoices.crawler.model_pipeline.SavePrizePipeline': 200
    },
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
}