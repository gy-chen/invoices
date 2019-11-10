import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoices.model import PrizeModel, InvoiceMatchModel
from invoices.job.match_prizes import PrizeMatcher

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
prize_model = PrizeModel(session)
invoice_match_model = InvoiceMatchModel(session)
prize_matcher = PrizeMatcher(prize_model, invoice_match_model)

prize_matcher.run()

session.commit()