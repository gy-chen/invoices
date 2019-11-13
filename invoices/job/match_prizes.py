from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoices.model import PrizeModel, InvoiceMatchModel
from invoices.model_prize_match import is_match, is_date_match


class PrizeMatcher:
    """class for fetching and matching stored prizes and invoices

    Args:
        prize_model (invoices.model.PrizeModel)
        invoice_model (invoices.model.InvoiceModel)
        invoice_match_model (invoices.model.InvoiceMatchModel)
    """

    def __init__(self, prize_model, invoice_match_model):
        self._prize_model = prize_model
        self._invoice_match_model = invoice_match_model

    def run(self):
        """Run prize matching job

        """
        invoices = self._invoice_match_model.get_unprocess_invoices()
        prizes = sorted(self._prize_model.get_prizes())
        for invoice in invoices:
            is_date_matched = False
            for prize in prizes:
                if is_match(prize, invoice):
                    self._invoice_match_model.add_invoice_match(
                        invoice.id, prize.type, prize.year, prize.month
                    )
                    break
                is_date_matched = is_date_matched or is_date_match(
                    prize.type,
                    prize.year,
                    prize.month,
                    invoice.type,
                    invoice.year,
                    invoice.month,
                )
            else:
                if is_date_matched:
                    self._invoice_match_model.add_invoice_unmatch(invoice.id)


def run_match_prizes_job(config):
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    prize_model = PrizeModel(session)
    invoice_match_model = InvoiceMatchModel(session)
    prize_matcher = PrizeMatcher(prize_model, invoice_match_model)

    prize_matcher.run()
    session.commit()
