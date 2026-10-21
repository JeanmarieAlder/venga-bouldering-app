from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    from venga_app.user_store import get_by_id

    return get_by_id(user_id)
