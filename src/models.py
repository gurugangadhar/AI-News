"""Data models for Personal AI Engineer Daily Digest."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RawItem:
    """Raw item fetched from any source."""

    source_name: str
    source_type: str  # rss | github | arxiv | twitter | etc.
    title: str
    content: str
    link: Optional[str] = None
    published: Optional[str] = None
    category: Optional[str] = None
    priority: str = "medium"  # high | medium | low
    raw_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoredItem:
    """Item scored for relevance and normalized for deduplication."""

    raw_item: RawItem
    score: float
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    canonical_url: str = ""
    normalized_title: str = ""
    content_hash: str = ""
    category: str = "ai_engineering"


@dataclass
class StoryCluster:
    """A cluster of items representing the same story across multiple outlets."""

    primary_item: ScoredItem
    alternative_items: List[ScoredItem] = field(default_factory=list)
    category: str = "ai_engineering"
    importance_score: float = 0.0

    @property
    def title(self) -> str:
        return self.primary_item.raw_item.title

    @property
    def link(self) -> Optional[str]:
        return self.primary_item.canonical_url or self.primary_item.raw_item.link

    @property
    def source_name(self) -> str:
        return self.primary_item.raw_item.source_name

    @property
    def all_sources(self) -> List[Dict[str, str]]:
        sources = [{"name": self.source_name, "url": self.link or ""}]
        for alt in self.alternative_items:
            url = alt.canonical_url or alt.raw_item.link or ""
            if url and url != self.link:
                sources.append({"name": alt.raw_item.source_name, "url": url})
        return sources


@dataclass
class StorySummary:
    """AI-generated senior briefing for a single story."""

    title: str
    what_happened: str
    why_it_matters: str
    developer_impact: str
    practical_takeaway: str
    primary_url: str
    source_name: str
    alternative_sources: List[Dict[str, str]] = field(default_factory=list)
    category: str = "ai_engineering"
    tags: List[str] = field(default_factory=list)
    is_updated: bool = False


@dataclass
class ProjectIdea:
    """Practical portfolio project idea derived from today's developments."""

    title: str
    description: str
    technologies: List[str] = field(default_factory=list)
    difficulty: str = "Intermediate"  # Beginner | Intermediate | Advanced
    portfolio_value: str = ""


@dataclass
class DigestContent:
    """Complete structured content for the daily digest."""

    digest_type: str  # morning | evening | test
    date_display: str  # e.g., "06 October 2026"
    period_label: str  # "Morning Briefing" | "Evening Briefing" | "Test Briefing"
    timezone: str = "Asia/Kolkata"
    generated_at: str = ""

    # Categorized stories
    top_stories: List[StorySummary] = field(default_factory=list)
    agentic_ai: List[StorySummary] = field(default_factory=list)
    models_llms: List[StorySummary] = field(default_factory=list)
    ai_engineering: List[StorySummary] = field(default_factory=list)
    ai_tools: List[StorySummary] = field(default_factory=list)
    cloud_ai: List[StorySummary] = field(default_factory=list)
    github_oss: List[StorySummary] = field(default_factory=list)
    research: List[StorySummary] = field(default_factory=list)

    # Actionable learning & career
    what_to_learn: List[str] = field(default_factory=list)
    project_idea: Optional[ProjectIdea] = None
    career_signals: List[str] = field(default_factory=list)

    # Secondary quick links
    quick_links: List[Dict[str, str]] = field(default_factory=list)

    is_quiet_window: bool = False
    stats: Dict[str, int] = field(default_factory=dict)
