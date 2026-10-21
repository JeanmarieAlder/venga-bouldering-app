import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be configured")
    
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.environ.get("FLASK_ENV") == "production"
    )

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
