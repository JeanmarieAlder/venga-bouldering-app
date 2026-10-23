from datetime import datetime

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from venga_app.ascent_store import (
    get_for_user,
    get_for_user_and_boulder,
    upsert_ascent,
)
from venga_app.boulder_store import get_all as get_all_boulders
from venga_app.blueprints.logbook import logbook_bp
from venga_app.blueprints.main.forms import BoulderEditForm


def _allowed_grades():
    # Reuse the grade choices already used by the boulder form.
    return {
        str(value)
        for value, _label in BoulderEditForm().grade.choices
    }


@logbook_bp.route("/logbook")
@login_required
def logbook():
    ascents = get_for_user(current_user.get_id())

    # Attach the current boulder details to each ascent.
    boulders_by_id = {
        str(boulder["id"]): boulder
        for boulder in get_all_boulders()
    }

    entries = []
    for ascent in ascents:
        boulder = boulders_by_id.get(str(ascent["boulder_id"]))

        # Keep old entries safe if a boulder no longer exists.
        if boulder is None:
            continue

        entries.append({
            **ascent,
            "boulder": boulder,
        })

    entries.sort(
        key=lambda entry: entry.get("completed_at", ""),
        reverse=True,
    )

    return render_template(
        "logbook/list.html",
        entries=entries,
    )


@logbook_bp.route(
    "/boulders/<boulder_id>/log-ascent",
    methods=["GET", "POST"],
)
@login_required
def log_ascent(boulder_id):
    boulder = next(
        (
            item
            for item in get_all_boulders()
            if str(item.get("id")) == str(boulder_id)
        ),
        None,
    )

    if boulder is None or not boulder.get("active", True):
        abort(404)

    user_id = current_user.get_id()
    existing = get_for_user_and_boulder(user_id, boulder_id)
    allowed_grades = _allowed_grades()
    errors = {}

    tries_value = (
        request.form.get("tries", "")
        if request.method == "POST"
        else str(existing["tries"]) if existing else "1"
    )
    personal_grade = (
        request.form.get("personal_grade", "")
        if request.method == "POST"
        else existing.get("personal_grade", boulder.get("grade", ""))
        if existing
        else boulder.get("grade", "")
    )

    if request.method == "POST":
        try:
            tries = int(tries_value)
            if tries < 1 or tries > 10000:
                errors["tries"] = "Enter a number of tries between 1 and 10000."
        except (TypeError, ValueError):
            tries = 0
            errors["tries"] = "Enter a valid whole number of tries."

        if personal_grade not in allowed_grades:
            errors["personal_grade"] = "Choose a valid grade."

        if not errors:
            upsert_ascent(
                user_id=user_id,
                boulder_id=boulder_id,
                tries=tries,
                personal_grade=personal_grade,
            )
            flash(
                "Ascent updated successfully."
                if existing
                else "Boulder added to your logbook!",
                "success",
            )
            return redirect(
                url_for("main.boulder_detail", boulder_id=boulder_id)
            )

        flash("Please correct the errors below.", "error")

    grade_choices = BoulderEditForm().grade.choices

    return render_template(
        "logbook/log_ascent.html",
        boulder=boulder,
        existing=existing,
        tries_value=tries_value,
        personal_grade=personal_grade,
        grade_choices=grade_choices,
        errors=errors,
    )