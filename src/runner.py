"""Main entry point for daily digest: preserves backward compatibility while running modern pipeline."""

import os
from pathlib import Path
from typing import Optional
import yaml

from src.cli import detect_digest_type
from src.fetchers import (
    RawItem,
    fetch_email,
    fetch_follow_builders_podcasts,
    fetch_follow_builders_x,
    fetch_gmail,
    fetch_rss,
    fetch_twitter,
    fetch_youtube,
    fetch_youtube_transcript,
)
from src.pipeline import collect_raw_items, run_digest_pipeline
from src.summarize import summarize


def load_config(config_path: str = "sources.yaml") -> dict:
    """Load sources.yaml or config/sources.yaml (backward compatibility)."""
    p = Path(config_path)
    if not p.exists():
        alt = Path("config/sources.yaml")
        if alt.exists():
            p = alt
        else:
            alt2 = Path("sources.example.yaml")
            if alt2.exists():
                p = alt2
            else:
                return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_sources(config_path: str = "sources.yaml") -> list:
    """Load sources list (backward compatibility)."""
    return load_config(config_path).get("sources", [])


def fetch_all(sources: list, global_max_entries: int = 3, global_max_age_days: int = 30) -> list:
    """Fetch all sources (backward compatibility)."""
    from src.config import SourceConfig
    sc_list = []
    for s in sources:
        if isinstance(s, dict):
            sc_list.append(SourceConfig(
                name=s.get("name", "Unnamed"),
                type=s.get("type", "rss"),
                url=s.get("url"),
                category=s.get("category", "ai_engineering"),
                priority=s.get("priority", "medium"),
                enabled=s.get("enabled", True),
                max_entries=min(s.get("max_entries", 3), global_max_entries),
                fetch_fulltext=s.get("fetch_fulltext", False),
                fulltext_chars=s.get("fulltext_chars", 8000),
                extra={k: v for k, v in s.items() if k not in {
                    "name", "type", "url", "category", "priority",
                    "enabled", "max_entries", "fetch_fulltext", "fulltext_chars"
                }}
            ))
    return collect_raw_items(sc_list, max_age_days=global_max_age_days)


def run(config_path: str = "sources.yaml", output_dir: str = "summaries", api_key: Optional[str] = None) -> str:
    """Execute digest pipeline and return summary path (backward compatibility)."""
    digest_type = detect_digest_type()
    dry_run = os.environ.get("DRY_RUN", "false").lower() in ("true", "1", "yes")

    digest = run_digest_pipeline(
        digest_type=digest_type,
        dry_run=dry_run,
        output_dir=output_dir,
    )
    return f"Completed {digest_type} digest with {len(digest.top_stories)} top stories."


if __name__ == "__main__":
    dtype = detect_digest_type()
    is_dry = os.environ.get("DRY_RUN", "false").lower() in ("true", "1", "yes")
    print(f"[RUNNER] Starting AI Engineer Daily Digest (Detected type: {dtype})")
    run_digest_pipeline(digest_type=dtype, dry_run=is_dry)
