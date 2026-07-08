import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


def send_reset_email(to_email, reset_url):
    """
    Send a password reset email. If MAIL_USERNAME/MAIL_PASSWORD aren't set,
    falls back to printing the reset link to the console so the flow is
    testable in local dev without any email setup.
    """
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("=" * 70)
        print("[MAIL] MAIL_USERNAME/MAIL_PASSWORD not set — printing reset link instead:")
        print(f"[MAIL] Reset link for {to_email}:")
        print(f"[MAIL] {reset_url}")
        print("=" * 70)
        return True

    subject = "Reset your FitGenie password"
    body = (
        f"Hi,\n\n"
        f"We received a request to reset your FitGenie password.\n\n"
        f"Click the link below to choose a new password. This link expires in 1 hour:\n"
        f"{reset_url}\n\n"
        f"If you didn't request this, you can safely ignore this email.\n\n"
        f"— FitGenie"
    )

    msg = MIMEMultipart()
    msg["From"] = MAIL_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_USERNAME, to_email, msg.as_string())
        print(f"[MAIL] Reset email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[MAIL] Failed to send reset email: {e}")
        # Fall back to console link so the user isn't locked out just because
        # email delivery failed (e.g. wrong SMTP credentials).
        print(f"[MAIL] Reset link for {to_email}: {reset_url}")
        return False