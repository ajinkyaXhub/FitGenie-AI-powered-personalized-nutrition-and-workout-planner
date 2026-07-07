import os

class Config:
    # Use environment variables on hosted platforms; fall back to local values
    SECRET_KEY = os.environ.get("SECRET_KEY", "AIzaSyDQrXOzKtsOuUrzt-Se41FgN8g2Hhe09nY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDQrXOzKtsOuUrzt-Se41FgN8g2Hhe09nY")

    # gemini-1.5-flash and all Gemini 1.0/1.5 models have been retired by Google (return 404).
    # Centralized here so future model migrations only need one change.
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # DATABASE_URL is set automatically by Render / Railway / Heroku.
    # Fix postgres:// -> postgresql:// for SQLAlchemy 1.4+
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "database.db"))
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  # survive connection drops