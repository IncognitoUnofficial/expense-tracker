from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ExpenseForm(FlaskForm):
    amount = DecimalField(
        "Amount", places=2, validators=[DataRequired(), NumberRange(min=0.01)]
    )
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    description = StringField("Description", validators=[Optional(), Length(max=255)])
    expense_date = DateField("Date", validators=[DataRequired()])

    def set_category_choices(self, categories):
        self.category_id.choices = [(c.id, c.name) for c in categories]
