from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.schema import ForeignKeyConstraint
from invoices.sqlalchemy import Base
from invoices.invoice.sqlalchemy_model import (
    Invoice,
    ModelAdapter as InvoiceModelAdapter,
)
from invoices.prize.sqlalchemy_model import Prize, ModelAdapter as PrizeModelAdapter
from invoices.common import Month, PrizeType
from invoices.invoice_match.model import InvoiceMatch as SharedInvoiceMatch


class ModelAdapter:
    def __init__(self, session):
        self._session = session
        self._invoice_model_adapter = InvoiceModelAdapter()
        self._prize_model_adapter = PrizeModelAdapter()

    def to_invoice_match(self, invoice_match):
        invoice = self._session.query(Invoice).get(invoice_match.invoice_id)
        prize = None
        if (
            invoice_match.prize_type
            and invoice_match.prize_year
            and invoice_match.prize_type
            and invoice_match.prize_number
        ):
            prize = self._session.query(Prize).get(
                (
                    invoice_match.prize_type,
                    invoice_match.prize_year,
                    invoice_match.prize_month,
                    invoice_match.prize_number,
                )
            )
        return SharedInvoiceMatch(
            self._invoice_model_adapter.to_invoice(invoice),
            prize and self._prize_model_adapter.to_prize(prize),
            prize is not None,
        )


class InvoiceMatch(Base):
    __tablename__ = "invoice_matches"

    invoice_id = Column(Integer, ForeignKey("invoices.id"), primary_key=True)
    prize_type = Column(Enum(PrizeType))
    prize_year = Column(Integer)
    prize_month = Column(Enum(Month))
    prize_number = Column(String)

    __table_args__ = (
        ForeignKeyConstraint(
            ["prize_type", "prize_year", "prize_month", "prize_number"],
            ["prizes.type", "prizes.year", "prizes.month", "prizes.number"],
        ),
    )

    def __init__(self, invoice_id, prize_type, prize_year, prize_month, prize_number):
        self.invoice_id = invoice_id
        self.prize_type = prize_type
        self.prize_year = prize_year
        self.prize_month = prize_month
        self.prize_number = prize_number

    def __iter__(self):
        yield from (
            self.invoice_id,
            self.prize_type,
            self.prize_year,
            self.prize_month,
            self.prize_number,
        )


class InvoiceMatchModel:
    def __init__(self, session):
        self._session = session
        self._model_adapter = ModelAdapter(session)
        self._invoice_model_adapter = InvoiceModelAdapter()

    def add_invoice_match(
        self, invoice_id, prize_type, prize_year, prize_month, prize_number
    ):
        invoice_match_model = InvoiceMatch(
            invoice_id, prize_type, prize_year, prize_month, prize_number
        )
        self._session.add(invoice_match_model)

    def add_invoice_unmatch(self, invoice_id):
        invoice_match_model = InvoiceMatch(invoice_id, None, None, None, None)
        self._session.add(invoice_match_model)

    def get_invoice_matches(self):
        invoice_match_models = self._session.query(InvoiceMatch).all()
        return list(map(self._model_adapter.to_invoice_match, invoice_match_models))

    def get_unprocess_invoices(self):
        invoice_models = (
            self._session.query(Invoice)
            .outerjoin(InvoiceMatch, Invoice.id == InvoiceMatch.invoice_id)
            .filter(InvoiceMatch.invoice_id == None)
            .all()
        )
        return list(map(self._invoice_model_adapter.to_invoice, invoice_models))
