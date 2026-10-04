"""Global deduplication and sent-story state management."""

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional


def _get_state_path() -> Path:
    if "NEWS_SUMMARY_STATE" in os.environ:
        return Path(os.environ["NEWS_SUMMARY_STATE"])
    # Default to data/state.json in repository, fallback to state.json
    local_data = Path("data/state.json")
    if local_data.parent.exists() or local_data.exists():
        return local_data
    if Path("state.json").exists():
        return Path("state.json")
    return Path("data/state.json")


_STATE_FILE = _get_state_path()
_DEFAULT_RETENTION_SECONDS = 14 * 86400  # 14 days


def normalize_title(title: str) -> str:
    """Normalize a title for robust duplicate matching."""
    if not title:
        return ""
    t = title.lower()
    # Remove brackets, tags, common prefixes
    t = re.sub(r"\[.*?\]|\(.*?\)", "", t)
    # Remove trailing source attribution like " - OpenAI", " | Simon Willison"
    t = re.sub(r"\s*[-–—|:]\s*[\w\s\.]+$", "", t)
    # Remove non-alphanumeric characters (keep basic letters and numbers)
    t = re.sub(r"[^\w\s]", " ", t)
    # Collapse whitespace
    return " ".join(t.split())


def compute_content_hash(text: str) -> str:
    """Compute sha256 hash of content."""
    clean = re.sub(r"\s+", " ", text or "").strip().lower()
    return hashlib.sha256(clean[:5000].encode("utf-8")).hexdigest()[:16]


def load() -> Dict[str, Any]:
    """Load the state file, migrating old structures if necessary."""
    path = _get_state_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("seenArticles", {})
                data.setdefault("seenTweets", {})
                data.setdefault("seenVideos", {})
                data.setdefault("sentStories", {})
                return data
        except Exception as e:
            print(f"[WARNING] Error reading state file {path}: {e}")

    return {
        "seenArticles": {},
        "seenTweets": {},
        "seenVideos": {},
        "sentStories": {},
    }


def save(state: Dict[str, Any], retention_seconds: int = _DEFAULT_RETENTION_SECONDS) -> None:
    """Save the state file with automatic expiration of old records."""
    path = _get_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - retention_seconds

    # Clean old seen items
    for ns in ("seenArticles", "seenTweets", "seenVideos"):
        state.setdefault(ns, {})
        state[ns] = {k: v for k, v in state[ns].items() if isinstance(v, (int, float)) and v > cutoff}

    # Clean old sent stories
    sent = state.setdefault("sentStories", {})
    cleaned_sent = {}
    for key, record in sent.items():
        if isinstance(record, dict):
            ts = record.get("last_sent", record.get("timestamp", 0))
            if ts > cutoff:
                cleaned_sent[key] = record
        elif isinstance(record, (int, float)) and record > cutoff:
            cleaned_sent[key] = {"last_sent": record}
    state["sentStories"] = cleaned_sent

    try:
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Failed to write state file {path}: {e}")


def is_seen(state: Dict[str, Any], namespace: str, key: str) -> bool:
    """Check if key has been seen in namespace (backward compatibility)."""
    return key in state.get(namespace, {})


def mark_seen(state: Dict[str, Any], namespace: str, key: str) -> None:
    """Mark key as seen in namespace (backward compatibility)."""
    state.setdefault(namespace, {})[key] = time.time()


def is_story_already_sent(
    state: Dict[str, Any],
    url: Optional[str] = None,
    title: Optional[str] = None,
    content_hash: Optional[str] = None,
    max_age_hours: float = 36.0,
) -> bool:
    """Check whether a story has already been sent recently in an email."""
    sent = state.get("sentStories", {})
    now = time.time()
    cutoff = now - (max_age_hours * 3600)

    # Check by URL
    if url and url in sent:
        rec = sent[url]
        last_sent = rec.get("last_sent", 0) if isinstance(rec, dict) else rec
        if last_sent > cutoff:
            return True

    # Check by normalized title
    if title:
        norm_t = normalize_title(title)
        title_key = f"title:{norm_t}"
        if norm_t and title_key in sent:
            rec = sent[title_key]
            last_sent = rec.get("last_sent", 0) if isinstance(rec, dict) else rec
            if last_sent > cutoff:
                return True

    # Check by content hash
    if content_hash:
        hash_key = f"hash:{content_hash}"
        if hash_key in sent:
            rec = sent[hash_key]
            last_sent = rec.get("last_sent", 0) if isinstance(rec, dict) else rec
            if last_sent > cutoff:
                return True

    return False


def record_story_sent(
    state: Dict[str, Any],
    url: Optional[str],
    title: str,
    digest_type: str,
    content_hash: Optional[str] = None,
    score: float = 0.0,
) -> None:
    """Record that a story was sent in an email digest."""
    sent = state.setdefault("sentStories", {})
    now = time.time()

    record = {
        "url": url or "",
        "title": title,
        "normalized_title": normalize_title(title),
        "content_hash": content_hash or "",
        "last_sent": now,
        "digest_type": digest_type,
        "score": score,
    }

    if url:
        sent[url] = record
        # Also mark seenArticles for backward compatibility
        mark_seen(state, "seenArticles", url)

    norm_t = normalize_title(title)
    if norm_t:
        sent[f"title:{norm_t}"] = record

    if content_hash:
        sent[f"hash:{content_hash}"] = record
