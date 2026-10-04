"""Fetcher for trending AI repositories on GitHub."""

import json
import urllib.error
import urllib.request
from typing import List, Optional

from src.models import RawItem


def fetch_github_trending(
    url: Optional[str] = None,
    source_name: str = "GitHub Trending AI",
    max_entries: int = 4,
    category: str = "github_oss",
    priority: str = "high",
) -> List[RawItem]:
    """Fetch top newly created / trending AI repositories via GitHub Search API."""
    query_url = url or "https://api.github.com/search/repositories?q=topic:ai-agent+topic:llm&sort=stars&order=desc"
    headers = {
        "User-Agent": "AIEngineerDigest/2.0",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        req = urllib.request.Request(query_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[WARNING] Could not fetch GitHub trending repos: {e}")
        return []

    items: List[RawItem] = []
    repos = data.get("items", [])
    for repo in repos[:max_entries]:
        full_name = repo.get("full_name", "")
        desc = repo.get("description", "No description provided.")
        stars = repo.get("stargazers_count", 0)
        html_url = repo.get("html_url", "")
        topics = repo.get("topics", [])

        title = f"{full_name} ({stars:,} stars)"
        content = f"{desc} | Topics: {', '.join(topics[:5])}"

        items.append(RawItem(
            source_name=source_name,
            source_type="github_trending",
            title=title,
            content=content,
            link=html_url,
            category=category,
            priority=priority,
            raw_metadata={"stars": stars, "topics": topics},
        ))

    return items
