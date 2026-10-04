"""Mock email sender for testing and local dry-runs."""

from pathlib import Path
from typing import List, Optional

from src.email.base import EmailSender


class MockEmailSender(EmailSender):
    """Simulates email delivery by logging and optionally writing to an HTML preview file."""

    def __init__(self, output_path: str = "summaries/latest_preview.html"):
        self.output_path = Path(output_path)
        self.sent_emails: List[dict] = []

    def send(
        self,
        subject: str,
        html_content: str,
        text_content: str,
        recipients: List[str],
        from_address: Optional[str] = None,
    ) -> bool:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(html_content, encoding="utf-8")

        print(f"[DRY-RUN / MOCK EMAIL] Subject: {subject}")
        print(f"[DRY-RUN / MOCK EMAIL] Recipients: {', '.join(recipients)}")
        print(f"[DRY-RUN / MOCK EMAIL] HTML preview saved to: {self.output_path.resolve()}")

        self.sent_emails.append({
            "subject": subject,
            "recipients": recipients,
            "html": html_content,
            "text": text_content,
        })
        return True
