from . import context
from .prize import PrizeTypeEnum as ItemPrizeTypeEnum
from .prize import PrizeMonthEnum as ItemPrizeMonthEnum
from invoices.model import PrizeTypeEnum, PrizeMonthEnum


class SavePrizePipeline:
    # TODO: may can use simpler way to convert this
    _ITEM_TYPE_MAPPING = {
        ItemPrizeTypeEnum.SPECIAL_TOP_AWARD: PrizeTypeEnum.SPECIAL_TOP_AWARD,
        ItemPrizeTypeEnum.TOP_AWARD: PrizeTypeEnum.TOP_AWARD,
        ItemPrizeTypeEnum.FIRST_AWARD: PrizeTypeEnum.FIRST_AWARD,
        ItemPrizeTypeEnum.SECOND_AWARD: PrizeTypeEnum.SECOND_AWARD,
        ItemPrizeTypeEnum.THIRD_AWARD: PrizeTypeEnum.THIRD_AWARD,
        ItemPrizeTypeEnum.FOURTH_AWARD: PrizeTypeEnum.FOURTH_AWARD,
        ItemPrizeTypeEnum.FIFTH_AWARD: PrizeTypeEnum.FIFTH_AWARD,
        ItemPrizeTypeEnum.SIXTH_AWARD: PrizeTypeEnum.SIXTH_AWARD,
        ItemPrizeTypeEnum.SPECIAL_SIXTH_AWARD: PrizeTypeEnum.SPECIAL_SIXTH_AWARD
    }

    _ITEM_MONTH_MAPPING = {
        ItemPrizeMonthEnum.MONTH_1_2: PrizeMonthEnum.MONTH_1_2,
        ItemPrizeMonthEnum.MONTH_3_4: PrizeMonthEnum.MONTH_3_4,
        ItemPrizeMonthEnum.MONTH_5_6: PrizeMonthEnum.MONTH_5_6,
        ItemPrizeMonthEnum.MONTH_7_8: PrizeMonthEnum.MONTH_7_8,
        ItemPrizeMonthEnum.MONTH_9_10: PrizeMonthEnum.MONTH_9_10,
        ItemPrizeMonthEnum.MONTH_11_12: PrizeMonthEnum.MONTH_11_12
    }

    def process_item(self, item, spider):
        prize_model = context.prize_model
        prize_model.add_prize(*self._to_prize_args(item))

    def _to_prize_args(self, item):
        return (
            self._to_prize_type(item['type']),
            item['year'],
            self._to_prize_month(item['month']),
            item['number'],
            self._to_prize(item['type'])
        )

    def _to_prize_type(self, prize_item_type):
        return self._ITEM_TYPE_MAPPING[prize_item_type]

    def _to_prize_month(self, prize_item_month):
        return self._ITEM_MONTH_MAPPING[prize_item_month]

    def _to_prize(self, prize_item_type):
        # TODO
        return 200