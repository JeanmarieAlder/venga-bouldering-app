
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class BoulderEditForm(FlaskForm):
    name = StringField(
        "Name",
        filters=[lambda value: value.strip() if isinstance(value, str) else value],
        validators=[DataRequired(), Length(max=100)],
    )

    grade = StringField(
        "Grade",
        filters=[lambda value: value.strip() if isinstance(value, str) else value],
        validators=[DataRequired(), Length(max=20)],
    )

    color = StringField(
        "Color",
        filters=[lambda value: value.strip() if isinstance(value, str) else value],
        validators=[DataRequired(), Length(max=50)],
    )

    setter = StringField(
        "Setter",
        filters=[lambda value: value.strip() if isinstance(value, str) else value],
        validators=[DataRequired(), Length(max=80)],
    )

    submit = SubmitField("Save changes")
