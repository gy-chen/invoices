from sqlalchemy import Column, Integer, String, Enum
from invoices.sqlalchemy import Base
from invoices.common import Month, PrizeType
from invoices.prize.model import Prize as SharedPrize
from invoices.prize.model import PrizeModel as SharedPrizeModel


class ModelAdapter:
    def to_prize(self, prize_model):
        return SharedPrize(*prize_model)


class Prize(Base):
    __tablename__ = "prizes"

    type = Column(Enum(PrizeType), primary_key=True)
    year = Column(Integer, primary_key=True)
    month = Column(Enum(Month), primary_key=True)
    number = Column(String, primary_key=True)
    prize = Column(Integer)

    def __init__(self, type, year, month, number, prize):
        self.type = type
        self.year = year
        self.month = month
        self.number = number
        self.prize = prize

    def __iter__(self):
        yield from (self.type, self.year, self.month, self.number, self.prize)


class PrizeModel(SharedPrizeModel):
    def __init__(self, session):
        self._session = session
        self._model_adapter = ModelAdapter()

    def add_prize(self, type, year, month, number, prize):
        prize_model = Prize(type, year, month, number, prize)
        self._session.add(prize_model)

    def delete_prize(self, type_, year, month, number):
        prize_model = self._session.query(Prize).get((type_, year, month, number))
        if not prize_model:
            raise ValueError("prize is not exists")
        self._session.delete(prize_model)

    def get_prizes(self):
        prize_models = self._session.query(Prize).all()
        return list(map(self._model_adapter.to_prize, prize_models))
