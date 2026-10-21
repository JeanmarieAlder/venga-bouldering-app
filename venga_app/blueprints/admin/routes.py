from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from venga_app.permissions import admin_required
from venga_app.user_store import get_all, update_user_role

from . import admin_bp


@admin_bp.route("/users")
@admin_required
def users():
    all_users = get_all()

    return render_template(
        "admin/users.html",
        users=all_users,
    )


@admin_bp.route("/users/<user_id>/role", methods=["POST"])
@admin_required
def change_role(user_id):
    new_role = request.form.get("role", "")

    if new_role not in {"climber", "setter"}:
        flash("Invalid role selected.", "error")
        return redirect(url_for("admin.users"))

    if not update_user_role(user_id, new_role):
        flash("Could not update this user's role.", "error")
        return redirect(url_for("admin.users"))

    flash("User role updated successfully.", "success")
    return redirect(url_for("admin.users"))