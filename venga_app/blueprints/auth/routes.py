
from urllib.parse import urlsplit

from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_babel import gettext as _

from venga_app.user_store import create_user, get_by_username
from . import auth_bp
from .forms import LoginForm, RegistrationForm


def safe_redirect_target(target):
    """Allow only local, absolute-path redirects."""
    if not target:
        return False

    parsed = urlsplit(target)

    return (
        not parsed.scheme
        and not parsed.netloc
        and target.startswith("/")
        and not target.startswith("//")
        and "\\" not in target
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()

    if form.validate_on_submit():

        username = form.username.data.strip()
        display_name = form.display_name.data.strip()
        if get_by_username(form.username.data):
            form.username.errors.append(_("Username already exists."))
        else:
            create_user(
                username=username,
                display_name=display_name,
                password=form.password.data,
            )

            flash(
                _("Your account has been created. You can log in now."),
                "success",
            )
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        user = get_by_username(username)

        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password."), "error")
        else:
            login_user(user, remember=form.remember_me.data)
            target = request.args.get("next")

            if safe_redirect_target(target):
                return redirect(target)

            return redirect(url_for("main.index"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash(_("You have been logged out."), "success")
    return redirect(url_for("main.index"))
