"""Abstract Base Class for email senders."""

from abc import ABC, abstractmethod
from typing import List, Optional


class EmailSender(ABC):
    """Abstract interface for sending email digests."""

    @abstractmethod
    def send(
        self,
        subject: str,
        html_content: str,
        text_content: str,
        recipients: List[str],
        from_address: Optional[str] = None,
    ) -> bool:
        """Send an email to recipients. Returns True on success, False on failure."""
        pass
