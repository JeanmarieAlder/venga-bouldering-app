
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


GRADE_CHOICES = [
    (grade, grade)
    for grade in [
        "4", "4+",
        "5", "5+",
        "6A", "6A+", "6B", "6B+", "6C", "6C+",
        "7A", "7A+", "7B", "7B+", "7C", "7C+",
        "8A", "8A+", "8B", "8B+", "8C", "8C+",
        "9A",
    ]
]

# Keep this list short and easy to scan.
COLOR_CHOICES = [
    ("Red", "Red"),
    ("Blue", "Blue"),
    ("Yellow", "Yellow"),
    ("Green", "Green"),
    ("Orange", "Orange"),
    ("Purple", "Purple"),
    ("Pink", "Pink"),
    ("Black", "Black"),
]


class BoulderEditForm(FlaskForm):
    name = StringField(
        "Name",
        filters=[lambda value: value.strip() if isinstance(value, str) else value],
        validators=[DataRequired(), Length(max=100)],
    )

    grade = SelectField(
        "Grade",
        choices=GRADE_CHOICES,
        validators=[DataRequired()],
    )

    color = SelectField(
        "Hold color",
        choices=COLOR_CHOICES,
        validators=[DataRequired()],
    )

    setter = StringField(
        "Setter",
        filters=[lambda value: value.strip() if isinstance(value, str) else value],
        validators=[DataRequired(), Length(max=80)],
    )

    photo = FileField("Boulder photo")

    submit = SubmitField("Save changes")
