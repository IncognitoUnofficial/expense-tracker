from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=80)])
