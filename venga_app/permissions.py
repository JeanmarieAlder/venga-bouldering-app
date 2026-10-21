from functools import wraps

from flask import abort, jsonify
from flask_login import current_user, login_required


def setter_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.can_set_boulders:
            return jsonify({
                "error": "Setter permissions required"
            }), 403

        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)

        return view(*args, **kwargs)

    return wrapped
