from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel

login_manager = LoginManager()
csrf = CSRFProtect()
babel = Babel()

login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    from venga_app.user_store import get_by_id

    return get_by_id(user_id)
