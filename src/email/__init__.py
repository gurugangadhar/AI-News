"""Email delivery module."""

from src.email.base import EmailSender
from src.email.factory import get_email_sender
from src.email.mock_sender import MockEmailSender
from src.email.resend_sender import ResendSender
from src.email.smtp_sender import SMTPSender

__all__ = ["EmailSender", "ResendSender", "SMTPSender", "MockEmailSender", "get_email_sender"]
