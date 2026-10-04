"""Fetcher for Hugging Face Daily Papers (practical AI research)."""

import json
import urllib.error
import urllib.request
from typing import List, Optional

from src.models import RawItem


def fetch_hf_papers(
    url: Optional[str] = None,
    source_name: str = "Hugging Face Daily Papers",
    max_entries: int = 3,
    category: str = "research",
    priority: str = "high",
) -> List[RawItem]:
    """Fetch top curated research papers from Hugging Face Daily Papers API."""
    query_url = url or "https://huggingface.co/api/daily_papers"
    headers = {
        "User-Agent": "AIEngineerDigest/2.0",
        "Accept": "application/json",
    }

    try:
        req = urllib.request.Request(query_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[WARNING] Could not fetch Hugging Face papers: {e}")
        return []

    items: List[RawItem] = []
    papers = data if isinstance(data, list) else data.get("papers", [])
    for p in papers[:max_entries]:
        paper_obj = p.get("paper", p)
        paper_id = paper_obj.get("id", "")
        title = paper_obj.get("title", "Untitled Research Paper")
        summary = paper_obj.get("summary", "")
        upvotes = p.get("upvotes", paper_obj.get("upvotes", 0))

        paper_url = f"https://huggingface.co/papers/{paper_id}" if paper_id else "https://huggingface.co/papers"
        content = f"{summary} (HF Upvotes: {upvotes})"

        items.append(RawItem(
            source_name=source_name,
            source_type="hf_papers",
            title=f"{title} ({upvotes} upvotes)" if upvotes else title,
            content=content,
            link=paper_url,
            category=category,
            priority=priority,
            raw_metadata={"upvotes": upvotes, "paper_id": paper_id},
        ))

    return items
