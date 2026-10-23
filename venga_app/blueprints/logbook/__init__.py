from flask import Blueprint

logbook_bp = Blueprint("logbook", __name__)

from venga_app.blueprints.logbook import routes