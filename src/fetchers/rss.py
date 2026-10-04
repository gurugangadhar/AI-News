"""RSS Fetcher: supports blogs, newsletters, feeds, and company release streams."""

import re
import time as _time
import urllib.request
from typing import List, Optional
import feedparser

from src.models import RawItem
from src import state as _state


def _fetch_fulltext(url: str, max_chars: int = 8000) -> Optional[str]:
    """Extract article body text with trafilatura if installed, otherwise None."""
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
        )
        if text and len(text) > max_chars:
            text = text[:max_chars] + "… (truncated)"
        return text
    except Exception:
        return None


def fetch_rss(
    url: str,
    source_name: str,
    max_entries: int = 3,
    fetch_fulltext: bool = False,
    fulltext_chars: int = 8000,
    max_age_days: int = 30,
    category: Optional[str] = None,
    priority: str = "medium",
) -> List[RawItem]:
    """Fetch RSS feed entries with age filtering and text extraction."""
    try:
        feed = feedparser.parse(
            url,
            request_headers={"User-Agent": "AIEngineerDigest/2.0 (+https://github.com/guo-yichen/news-summary)"}
        )
    except Exception as e:
        print(f"[WARNING] Failed to fetch RSS from '{source_name}' ({url}): {e}")
        return []

    if getattr(feed, "bozo", 0) and not feed.entries:
        bozo_exc = getattr(feed, "bozo_exception", "Unknown parse issue")
        print(f"[WARNING] Feed '{source_name}' has parsing error: {bozo_exc}")
        return []

    st = _state.load()
    new_items: List[RawItem] = []
    age_cutoff = _time.time() - (max_age_days * 86400)

    for entry in feed.entries:
        if len(new_items) >= max_entries:
            break

        title = entry.get("title", "(Untitled)").strip()
        link = entry.get("link", "").strip()
        published = entry.get("published", entry.get("updated", ""))

        # Check published date against cutoff if available
        published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if published_parsed:
            try:
                pub_ts = _time.mktime(published_parsed)
                if pub_ts < age_cutoff:
                    continue
            except Exception:
                pass

        # Substack and WordPress store full text in content:encoded
        content_entries = entry.get("content", [])
        if content_entries:
            summary = content_entries[0].get("value", "")
        else:
            summary = entry.get("summary", entry.get("description", ""))

        # Strip HTML tags from summary
        if summary and "<" in summary:
            summary = re.sub(r"<[^>]+>", " ", summary)
            summary = " ".join(summary.split())

        # Fulltext extraction if summary is too short
        content = summary if len(summary) >= 200 else None
        if fetch_fulltext and link and not content:
            content = _fetch_fulltext(link, max_chars=fulltext_chars)
            if not content:
                content = summary

        if content and len(content) > fulltext_chars:
            content = content[:fulltext_chars] + "… (truncated)"

        new_items.append(RawItem(
            source_name=source_name,
            source_type="rss",
            title=title,
            content=content or title,
            link=link or None,
            published=published or None,
            category=category,
            priority=priority,
        ))

    return new_items
