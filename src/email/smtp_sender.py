"""Email sender via SMTP (Gmail App Password, AWS SES, or custom SMTP)."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from src.config import AppConfig
from src.email.base import EmailSender


class SMTPSender(EmailSender):
    """Sends emails using standard SMTP / SMTP_SSL."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.host = config.smtp_host or "smtp.gmail.com"
        self.port = config.smtp_port or 465
        self.user = config.smtp_user
        self.password = config.smtp_password
        self.from_address = config.email_from or self.user or ""

    def send(
        self,
        subject: str,
        html_content: str,
        text_content: str,
        recipients: List[str],
        from_address: Optional[str] = None,
    ) -> bool:
        if not self.user or not self.password:
            print("[ERROR] SMTP_USER or SMTP_PASSWORD not configured.")
            return False

        if not recipients:
            print("[ERROR] No recipients specified for SMTP delivery.")
            return False

        sender = from_address or self.from_address or self.user

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Personal AI Engineer Digest <{sender}>" if "<" not in sender else sender
        msg["To"] = ", ".join(recipients)

        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            if self.port == 465:
                with smtplib.SMTP_SSL(self.host, self.port, timeout=30) as server:
                    server.login(self.user, self.password)
                    server.sendmail(sender, recipients, msg.as_bytes())
            else:
                with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                    server.starttls()
                    server.login(self.user, self.password)
                    server.sendmail(sender, recipients, msg.as_bytes())

            print(f"[SUCCESS] Email delivered via SMTP to {len(recipients)} recipients.")
            return True
        except Exception as e:
            print(f"[ERROR] SMTP delivery failed: {e}")
            return False
