"""Factory for creating EmailSender instances."""

import os
from src.config import AppConfig
from src.email.base import EmailSender
from src.email.mock_sender import MockEmailSender
from src.email.resend_sender import ResendSender
from src.email.smtp_sender import SMTPSender


def get_email_sender(config: AppConfig, dry_run: bool = False) -> EmailSender:
    """Return configured email sender instance."""
    if dry_run:
        return MockEmailSender()

    provider = (
        os.environ.get("EMAIL_PROVIDER") or config.email_provider or "resend"
    ).lower().strip()

    if provider == "mock":
        return MockEmailSender()

    if provider == "resend":
        if os.environ.get("RESEND_API_KEY") or config.resend_api_key:
            return ResendSender(config)
        # Check if SMTP is configured as fallback
        if (os.environ.get("EMAIL_USER") or config.smtp_user) and (os.environ.get("EMAIL_PASSWORD") or config.smtp_password):
            print("[INFO] RESEND_API_KEY not found; falling back to SMTP sender.")
            return SMTPSender(config)
        print("[WARNING] Neither Resend nor SMTP credentials found. Falling back to MockEmailSender.")
        return MockEmailSender()

    if provider in ("smtp", "gmail"):
        if (os.environ.get("EMAIL_USER") or config.smtp_user) and (os.environ.get("EMAIL_PASSWORD") or config.smtp_password):
            return SMTPSender(config)
        print("[WARNING] SMTP credentials missing. Falling back to MockEmailSender.")
        return MockEmailSender()

    return MockEmailSender()
