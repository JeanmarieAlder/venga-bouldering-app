from datetime import datetime, timezone

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import login_required

from venga_app.boulder_store import get_all, get_by_id, save_all
from venga_app.permissions import setter_required

from . import main_bp
from .forms import BoulderEditForm


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/boulders")
@login_required
def boulder_list():
    boulders = [
        boulder for boulder in get_all()
        if boulder.get("active", True)
    ]

    return render_template(
        "boulders/list.html",
        boulders=boulders,
    )


@main_bp.route("/boulders/<boulder_id>")
@login_required
def boulder_detail(boulder_id):
    boulder = get_by_id(boulder_id)

    if not boulder or not boulder.get("active", True):
        abort(404)

    return render_template(
        "boulders/detail.html",
        boulder=boulder,
    )


@main_bp.route("/boulders/<boulder_id>/edit", methods=["GET", "POST"])
@setter_required
def edit_boulder(boulder_id):
    boulders = get_all()

    boulder = next(
        (
            item for item in boulders
            if item.get("id") == boulder_id
        ),
        None,
    )

    if not boulder or not boulder.get("active", True):
        abort(404)

    form = BoulderEditForm()

    if form.validate_on_submit():
        boulder.update({
            "name": form.name.data,
            "grade": form.grade.data,
            "color": form.color.data,
            "setter": form.setter.data,
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        })

        save_all(boulders)

        flash("Boulder updated successfully.", "success")

        return redirect(
            url_for(
                "main.boulder_detail",
                boulder_id=boulder_id,
            )
        )

    # Populate the form from the existing boulder on GET.
    # Also repopulate from storage when a POST fails validation.
    if not form.is_submitted():
        form.name.data = boulder.get("name", "")
        form.grade.data = boulder.get("grade", "")
        form.color.data = boulder.get("color", "")
        form.setter.data = boulder.get("setter", "")

    return render_template(
        "boulders/edit.html",
        boulder=boulder,
        form=form,
    )
