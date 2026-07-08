import os
import secrets

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; env vars must be set another way

class Config:
    # SECRET_KEY: use env var in production; auto-generate a random one locally
    # if not set (sessions just won't survive a server restart, which is fine for dev).
    # NEVER hardcode a real secret here — this file is checked into a public repo.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    # GEMINI_API_KEY must be set via environment variable. There is no hardcoded
    # fallback on purpose: a previous hardcoded key was leaked by being committed
    # to this repo, and Google auto-revoked it as a result.
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get a key from https://aistudio.google.com/apikey and set it as an "
            "environment variable (locally: a .env file with python-dotenv, or "
            "`set GEMINI_API_KEY=...` in PowerShell for this session; on your "
            "host: Render/Railway/Vercel's dashboard 'Environment Variables' section)."
        )

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