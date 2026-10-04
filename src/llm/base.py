"""Abstract Base Class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from src.models import DigestContent, ProjectIdea, StoryCluster, StorySummary


class LLMProvider(ABC):
    """Abstract interface for LLM operations in the digest pipeline."""

    @abstractmethod
    def summarize_digest(
        self,
        clusters: List[StoryCluster],
        digest_type: str,
        date_str: str,
        role_targets: List[str],
        priority_topics: List[str],
    ) -> DigestContent:
        """Summarize selected story clusters into structured DigestContent."""
        pass
