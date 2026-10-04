"""Email sender via Resend API."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import List, Optional

from src.config import AppConfig
from src.email.base import EmailSender


class ResendSender(EmailSender):
    """Sends emails using the modern Resend REST API."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.api_key = config.resend_api_key or os.environ.get("RESEND_API_KEY")
        self.from_address = config.email_from or "onboarding@resend.dev"

    def send(
        self,
        subject: str,
        html_content: str,
        text_content: str,
        recipients: List[str],
        from_address: Optional[str] = None,
    ) -> bool:
        if not self.api_key:
            print("[ERROR] RESEND_API_KEY is not configured.")
            return False

        if not recipients:
            print("[ERROR] No recipients specified for email delivery.")
            return False

        sender = from_address or self.from_address
        # Format sender with display name if not already formatted
        if "<" not in sender and "@" in sender:
            sender = f"Personal AI Engineer Digest <{sender}>"

        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AIEngineerDigest/2.0",
        }
        payload = {
            "from": sender,
            "to": recipients,
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    email_id = resp_data.get("id", "unknown")
                    print(f"[SUCCESS] Email successfully delivered via Resend. ID: {email_id}")
                    return True
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8", errors="replace")
                print(f"[Resend API Error {e.code}] Attempt {attempt + 1}/3: {err_msg}")
                if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue
                return False
            except Exception as e:
                print(f"[Resend Network Error] Attempt {attempt + 1}/3: {e}")
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue
                return False

        return False
