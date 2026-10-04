"""Deduplication and story clustering engine."""

import re
from typing import Dict, List, Set, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from src.models import ScoredItem, StoryCluster
from src.state import normalize_title


TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_name", "fbclid", "gclid", "ref", "source", "feature", "ocid", "cmpid"
}


def canonicalize_url(url: str) -> str:
    """Strip tracking params, fragments, and normalize URL."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        # Filter query params
        q_pairs = [
            (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k.lower() not in TRACKING_PARAMS
        ]
        new_query = urlencode(q_pairs)
        # Normalize path: remove trailing slash unless root
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"
        # Force scheme to lowercase
        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        clean = urlunparse((scheme, netloc, path, parsed.params, new_query, ""))
        return clean
    except Exception:
        return url.strip()


def tokenize_title(title: str) -> Set[str]:
    """Tokenize normalized title into meaningful words."""
    norm = normalize_title(title)
    words = re.findall(r"\b[a-z0-9_-]{2,}\b", norm)
    # Stop words
    stop_words = {
        "the", "and", "for", "with", "from", "that", "this", "are", "was",
        "about", "into", "over", "after", "how", "what", "why", "when",
        "where", "who", "will", "can", "has", "have", "had", "new", "announces",
        "releases", "launches", "introducing", "update", "latest"
    }
    return {w for w in words if w not in stop_words}


def calculate_title_similarity(title1: str, title2: str) -> float:
    """Compute token Jaccard/containment similarity and character n-gram overlap between two titles."""
    tokens1 = tokenize_title(title1)
    tokens2 = tokenize_title(title2)

    if not tokens1 or not tokens2:
        return 0.0

    # Token Jaccard & Containment
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    jaccard = len(intersection) / len(union) if union else 0.0
    min_tokens = min(len(tokens1), len(tokens2))
    containment = (len(intersection) / min_tokens) if min_tokens > 0 else 0.0
    token_score = max(jaccard, 0.8 * containment) if min_tokens >= 3 else jaccard

    # Character bigram similarity for typo / inflection tolerance
    s1 = normalize_title(title1)
    s2 = normalize_title(title2)
    if s1 == s2 and len(s1) > 0:
        return 1.0

    bigrams1 = {s1[i:i+2] for i in range(len(s1)-1)}
    bigrams2 = {s2[i:i+2] for i in range(len(s2)-1)}
    bg_overlap = 0.0
    if bigrams1 and bigrams2:
        bg_overlap = (2.0 * len(bigrams1.intersection(bigrams2))) / (len(bigrams1) + len(bigrams2))

    # Weighted blend
    return (0.7 * token_score) + (0.3 * bg_overlap)


def cluster_stories(
    items: List[ScoredItem],
    similarity_threshold: float = 0.45,
) -> List[StoryCluster]:
    """Cluster stories to ensure each real-world event is represented only once."""
    if not items:
        return []

    # Sort descending by score initially so highest-scoring / official sources become primary
    sorted_items = sorted(items, key=lambda x: x.score, reverse=True)
    clusters: List[StoryCluster] = []

    for item in sorted_items:
        c_url = item.canonical_url or item.raw_item.link or ""
        matched_cluster = None

        for cluster in clusters:
            prim_url = cluster.primary_item.canonical_url or cluster.primary_item.raw_item.link or ""

            # 1. Exact canonical URL match
            if c_url and prim_url and c_url == prim_url:
                matched_cluster = cluster
                break

            # 2. High title similarity
            sim = calculate_title_similarity(item.raw_item.title, cluster.primary_item.raw_item.title)
            if sim >= similarity_threshold:
                matched_cluster = cluster
                break

            # Also check against alternative items in this cluster
            for alt in cluster.alternative_items:
                alt_url = alt.canonical_url or alt.raw_item.link or ""
                if c_url and alt_url and c_url == alt_url:
                    matched_cluster = cluster
                    break
                if calculate_title_similarity(item.raw_item.title, alt.raw_item.title) >= similarity_threshold:
                    matched_cluster = cluster
                    break
            if matched_cluster:
                break

        if matched_cluster:
            matched_cluster.alternative_items.append(item)
            # If incoming item is from an official source and current primary is not, promote it
            is_new_official = item.raw_item.priority == "high"
            is_curr_official = matched_cluster.primary_item.raw_item.priority == "high"
            if is_new_official and not is_curr_official:
                matched_cluster.alternative_items.remove(item)
                matched_cluster.alternative_items.append(matched_cluster.primary_item)
                matched_cluster.primary_item = item
                matched_cluster.category = item.category
        else:
            clusters.append(StoryCluster(
                primary_item=item,
                alternative_items=[],
                category=item.category,
                importance_score=item.score,
            ))

    # Recalculate cluster score: primary score + small boost for multi-source confirmation
    for cluster in clusters:
        multi_boost = min(len(cluster.alternative_items) * 3.0, 10.0)
        cluster.importance_score = cluster.primary_item.score + multi_boost

    # Sort clusters by importance score descending
    clusters.sort(key=lambda c: c.importance_score, reverse=True)
    return clusters
