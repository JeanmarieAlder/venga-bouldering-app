from flask import Flask, render_template, session, request

from venga_app.extensions import csrf, login_manager, babel


def select_locale():
    supported_languages = ["en", "fr"]

    language = session.get("language")

    if language in supported_languages:
        return language

    return request.accept_languages.best_match(supported_languages) or "en"

def create_app():
    app = Flask(__name__)
    app.config.from_object("venga_app.config.Config")

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    login_manager.init_app(app)
    csrf.init_app(app)

    app.config["BABEL_TRANSLATION_DIRECTORIES"] = "../translations"
    babel.init_app(app, locale_selector=select_locale)

    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return render_template("csrf_error.html"), 400

    from venga_app.blueprints.boulder import boulder_bp
    app.register_blueprint(boulder_bp)

    from venga_app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    from venga_app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from venga_app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    from venga_app.blueprints.logbook import logbook_bp
    app.register_blueprint(logbook_bp)

    return app