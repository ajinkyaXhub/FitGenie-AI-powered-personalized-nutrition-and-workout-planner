from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from config import Config

RESET_SALT = "password-reset-salt"


def generate_reset_token(user_email):
    """Create a signed, timestamped token embedding the user's email."""
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(user_email, salt=RESET_SALT)


def verify_reset_token(token, max_age_seconds=3600):
    """
    Decode a reset token and return the embedded email, or None if it's
    invalid or expired (default expiry: 1 hour).
    """
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(token, salt=RESET_SALT, max_age=max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None
    return email