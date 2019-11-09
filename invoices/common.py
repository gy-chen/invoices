import enum


class PrizeType(enum.Enum):
    SPECIAL_TOP_AWARD = 1
    TOP_AWARD = 2
    FIRST_AWARD = 3
    SECOND_AWARD = 4
    THIRD_AWARD = 5
    FOURTH_AWARD = 6
    FIFTH_AWARD = 7
    SIXTH_AWARD = 8
    SPECIAL_SIXTH_AWARD = 9


class Month(enum.Enum):
    MONTH_1_2 = 1
    MONTH_3_4 = 2
    MONTH_5_6 = 3
    MONTH_7_8 = 4
    MONTH_9_10 = 5
    MONTH_11_12 = 6