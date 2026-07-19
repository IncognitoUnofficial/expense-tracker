from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=80)])
    monthly_budget = DecimalField(
        "Monthly budget (optional)",
        places=2,
        validators=[Optional(), NumberRange(min=0.01)],
    )
