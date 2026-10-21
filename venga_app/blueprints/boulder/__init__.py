from flask import Blueprint

boulder_bp = Blueprint(
    "boulder",
    __name__,
    url_prefix="/api/boulders",
)

from venga_app.blueprints.boulder import routes