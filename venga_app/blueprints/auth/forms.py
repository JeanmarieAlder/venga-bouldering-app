from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
)


class RegistrationForm(FlaskForm):
    username = StringField(
        _l("Username"),
        validators=[
            DataRequired(),
            Length(min=3, max=30),
        ],
    )

    display_name = StringField(
        _l("Display name"),
        validators=[
            DataRequired(),
            Length(max=80),
        ],
    )

    password = PasswordField(
        _l("Password"),
        validators=[
            DataRequired(),
            Length(min=8, max=128),
        ],
    )

    confirm_password = PasswordField(
        _l("Confirm password"),
        validators=[
            DataRequired(),
            EqualTo("password", message=_l("Passwords must match.")),
        ],
    )

    submit = SubmitField(_l("Create account"))


class LoginForm(FlaskForm):
    username = StringField(
        _l("Username"),
        validators=[DataRequired()],
    )

    password = PasswordField(
        _l("Password"),
        validators=[DataRequired()],
    )

    remember_me = BooleanField(_l("Remember me"))

    submit = SubmitField(_l("Log in"))