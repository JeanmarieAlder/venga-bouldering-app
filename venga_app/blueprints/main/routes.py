import uuid
import json
from datetime import datetime, timezone

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from venga_app.boulder_store import get_all, get_by_id, save_all
from venga_app.permissions import setter_required
from venga_app.image_store import save_boulder_photo
from venga_app.ascent_store import get_for_user_and_boulder, get_for_user

from . import main_bp
from .forms import BoulderEditForm



@main_bp.route("/")
def index():
    stats = {
        "total_sent": 0,
        "total_tries": 0,
        "best_grade": None,
        "average_tries": None,
        "recent_sends": [],
        "grade_chart_labels": [],
        "grade_chart_counts": [],
    }

    if current_user.is_authenticated:
        ascents = get_for_user(current_user.get_id())
        boulders = get_all()

        boulders_by_id = {
            str(boulder["id"]): boulder
            for boulder in boulders
        }

        # Only count ascents whose boulder still exists.
        entries = []
        for ascent in ascents:
            boulder = boulders_by_id.get(
                str(ascent.get("boulder_id"))
            )

            if boulder is not None:
                entries.append({
                    **ascent,
                    "boulder": boulder,
                })

        # Use the same ordered grade choices as the boulder form.
        grade_choices = BoulderEditForm().grade.choices
        grade_order = {
            str(value): index
            for index, (value, _label) in enumerate(grade_choices)
        }

        # Count successful boulders by official grade.
        grade_counts = {grade: 0 for grade in grade_order}

        for entry in entries:
            official_grade = entry["boulder"].get("grade")

            if official_grade in grade_counts:
                grade_counts[official_grade] += 1

        # Keep the grades in the order defined by BoulderEditForm.
        grade_chart_labels = [
            grade for grade in grade_order
            if grade_counts[grade] > 0
        ]

        grade_chart_counts = [
            grade_counts[grade] for grade in grade_chart_labels
        ]

        total_sent = len(entries)
        total_tries = sum(
            int(entry.get("tries", 0))
            for entry in entries
        )

        official_grades = [
            entry["boulder"].get("grade")
            for entry in entries
            if entry["boulder"].get("grade") in grade_order
        ]

        best_grade = (
            max(official_grades, key=lambda grade: grade_order[grade])
            if official_grades
            else None
        )

        stats = {
            "total_sent": total_sent,
            "total_tries": total_tries,
            "best_grade": best_grade,
            "average_tries": (
                round(total_tries / total_sent, 1)
                if total_sent
                else None
            ),
            "recent_sends": sorted(
                entries,
                key=lambda entry: entry.get("completed_at", ""),
                reverse=True,
            )[:5],
            "grade_chart_labels": grade_chart_labels,
            "grade_chart_counts": grade_chart_counts,
        }

    return render_template("index.html", stats=stats)



@main_bp.route("/boulders")
@login_required
def boulder_list():
    boulders = [
        boulder
        for boulder in get_all()
        if boulder.get("active", True)
    ]

    boulders.sort(
        key=lambda boulder: boulder.get("created_at", ""),
        reverse=True,
    )

    return render_template(
        "boulders/list.html",
        boulders=boulders,
    )


@main_bp.route("/boulders/<boulder_id>")
@login_required
def boulder_detail(boulder_id):
    boulder = get_by_id(boulder_id)

    my_ascent = None

    if current_user.is_authenticated:
        my_ascent = get_for_user_and_boulder(
            current_user.get_id(),
            boulder_id,
        )

    if not boulder:
        abort(404)

    # to log ascents
    has_logged_ascent = False
    if current_user.is_authenticated:
        has_logged_ascent = (
            get_for_user_and_boulder(
                current_user.get_id(),
                boulder_id,
            )
            is not None
        )

    # to get users personal grade
    

    return render_template(
        "boulders/detail.html",
        boulder=boulder,
        my_ascent=my_ascent,
        has_logged_ascent=has_logged_ascent,
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
        if form.photo.data:
            try:
                boulder["photo"] = save_boulder_photo(form.photo.data)
            except ValueError as error:
                form.photo.errors.append(str(error))
                return render_template(
                    "boulders/edit.html",
                    form=form,
                    boulder=boulder,
                )
            
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


@main_bp.route("/boulders/new", methods=["GET", "POST"])
@setter_required
def create_boulder():
    form = BoulderEditForm()

    if not form.is_submitted():
        form.setter.data = current_user.display_name


    if form.validate_on_submit():

        # Get the picture from the camera input, if provided.
        camera_photo = request.files.get("photo_camera")

        # Prefer the camera picture; otherwise use the uploaded picture.
        if camera_photo and camera_photo.filename:
            photo_upload = camera_photo
        else:
            photo_upload = form.photo.data

        # Picture validation
        if not photo_upload or not photo_upload.filename:
            form.photo.errors.append(
                "Please upload a picture or take one with your camera."
            )
            return render_template(
                "boulders/create.html",
                form=form,
            )

        try:
            photo_path = save_boulder_photo(photo_upload)
        except ValueError as error:
            form.photo.errors.append(str(error))
            return render_template(
                "boulders/create.html",
                form=form,
            )


            
        now = datetime.now(timezone.utc).isoformat()

        boulder = {
            "id": str(uuid.uuid4()),
            "name": form.name.data,
            "grade": form.grade.data,
            "color": form.color.data,
            "setter": form.setter.data,
            "photo": photo_path,
            "created_at": now,
            "active": True,
            "archived_at": None,
        }

        boulders = get_all()
        boulders.append(boulder)
        save_all(boulders)

        flash("Boulder created successfully.", "success")

        return redirect(
            url_for(
                "main.boulder_detail",
                boulder_id=boulder["id"],
            )
        )

    return render_template(
        "boulders/create.html",
        form=form,
    )


@main_bp.route("/boulders/<boulder_id>/holds", methods=["GET", "POST"])
@login_required
@setter_required
def mark_holds(boulder_id):
    boulders = get_all()

    boulder = next(
        (
            item for item in boulders
            if item.get("id") == boulder_id
        ),
        None,
    )

    if boulder is None:
        abort(404)

    if not boulder.get("photo"):
        flash("Upload a photo before marking holds.", "error")
        return redirect(
            url_for("main.edit_boulder", boulder_id=boulder_id)
        )

    return_to = request.values.get("return_to", "edit")

    # Only allow known destinations.
    if return_to not in ("edit", "detail"):
        return_to = "edit"

    if request.method == "POST":
        
        try:
            holds = json.loads(request.form.get("holds_json", "[]"))

            if not isinstance(holds, list) or len(holds) > 500:
                raise ValueError("Invalid number of holds.")

            clean_holds = []
            type_counts = {"start": 0, "finish": 0}

            for hold in holds:
                if not isinstance(hold, dict):
                    raise ValueError("Invalid hold.")

                x = hold.get("x")
                y = hold.get("y")
                hold_type = hold.get("type", "regular")

                if (
                    isinstance(x, bool)
                    or isinstance(y, bool)
                    or not isinstance(x, (int, float))
                    or not isinstance(y, (int, float))
                    or not 0 <= x <= 1
                    or not 0 <= y <= 1
                ):
                    raise ValueError("Invalid hold position.")

                if hold_type not in ("regular", "start", "finish"):
                    raise ValueError("Invalid hold type.")

                if hold_type in type_counts:
                    type_counts[hold_type] += 1

                    if type_counts[hold_type] > 2:
                        raise ValueError(
                            "A boulder can have at most two "
                            "starting holds and two finishing holds."
                        )

                clean_holds.append({
                    "x": float(x),
                    "y": float(y),
                    "type": hold_type,
                })

        except (ValueError, TypeError, json.JSONDecodeError):
            flash("Could not save the hold positions. Check the hold types and limits.", "error")
            return redirect(
                url_for(
                    "main.mark_holds",
                    boulder_id=boulder_id,
                    return_to=return_to,
                )
            )


        boulder["holds"] = clean_holds
        save_all(boulders)

        flash("Hold positions saved successfully.", "success")

        if return_to == "detail":
            return redirect(
                url_for("main.boulder_detail", boulder_id=boulder_id)
            )

        return redirect(
            url_for("main.edit_boulder", boulder_id=boulder_id)
        )

    return render_template(
        "boulders/mark_holds.html",
        boulder=boulder,
        return_to=return_to,
    )