from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length
from invoices.common import Month


def _month_to_enum(month):
    month_map = {
        1: Month.MONTH_1_2,
        2: Month.MONTH_3_4,
        3: Month.MONTH_5_6,
        4: Month.MONTH_7_8,
        5: Month.MONTH_9_10,
        6: Month.MONTH_11_12,
    }
    return month_map[month]


class AddInvoiceForm(FlaskForm):
    year = IntegerField("year", validators=[DataRequired(), NumberRange(100, 200)])
    month = IntegerField("month", validators=[DataRequired(), NumberRange(1, 6)])
    number = StringField("number", validators=[DataRequired(), Length(8, 8)])
    note = StringField("note", default="")

    def __iter__(self):
        yield from (
            self.year.data,
            _month_to_enum(self.month.data),
            self.number.data,
            self.note.data,
        )


class UpdateInvoiceForm(FlaskForm):
    id = IntegerField("id", validators=[DataRequired()])
    year = IntegerField("year", validators=[DataRequired(), NumberRange(100, 200)])
    month = IntegerField("month", validators=[DataRequired(), NumberRange(1, 6)])
    number = StringField("number", validators=[DataRequired(), Length(8, 8)])
    note = StringField("note", validators=[DataRequired()])

    def __iter__(self):
        yield from (
            self.id.data,
            self.year.data,
            _month_to_enum(self.month.data),
            self.number.data,
            self.note.data,
        )


class GetInvoicesForm(FlaskForm):
    offset = IntegerField("offset", validators=[NumberRange(min=0)], default=0)
    per_page = IntegerField(
        "per_page", validators=[NumberRange(min=0, max=40)], default=20
    )

    def __iter__(self):
        yield from (self.offset.data, self.per_page.data)


class GetProcessedInvoicesForm(FlaskForm):
    offset = IntegerField("offset", validators=[NumberRange(min=0)], default=0)
    per_page = IntegerField(
        "per_page", validators=[NumberRange(min=0, max=40)], default=20
    )

    def __iter__(self):
        yield from (self.offset.data, self.per_page.data)
