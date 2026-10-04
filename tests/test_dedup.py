"""Unit tests for URL canonicalization, title similarity, and story clustering."""

import pytest
from src.dedup import calculate_title_similarity, canonicalize_url, cluster_stories
from src.models import RawItem, ScoredItem


def test_canonicalize_url():
    raw_url = "https://www.openai.com/index/introducing-canvas/?utm_source=twitter&utm_medium=social#details"
    clean = canonicalize_url(raw_url)
    assert "utm_source" not in clean
    assert "utm_medium" not in clean
    assert "#details" not in clean
    assert clean == "https://openai.com/index/introducing-canvas"


def test_title_similarity_identical():
    t1 = "Anthropic Releases Claude 3.7 Sonnet with Hybrid Reasoning"
    t2 = "Anthropic releases Claude 3.7 Sonnet with hybrid reasoning"
    sim = calculate_title_similarity(t1, t2)
    assert sim >= 0.95


def test_title_similarity_rephrased():
    t1 = "OpenAI Introduces Operator Agent for Web Automation"
    t2 = "OpenAI Launches Operator: Autonomous Agent for Browser Tasks"
    sim = calculate_title_similarity(t1, t2)
    assert sim >= 0.50


def test_title_similarity_unrelated():
    t1 = "DeepSeek Releases V3 Architecture Details"
    t2 = "Cursor AI Adds Windsurf Migration Feature"
    sim = calculate_title_similarity(t1, t2)
    assert sim < 0.25


def test_cluster_stories_merges_duplicates():
    item1 = ScoredItem(
        raw_item=RawItem(
            source_name="Anthropic Official",
            source_type="rss",
            title="Introducing Claude 3.7 Sonnet",
            content="Official launch of Claude 3.7 Sonnet model with reasoning.",
            link="https://www.anthropic.com/news/claude-3-7-sonnet",
            priority="high",
        ),
        score=45.0,
        canonical_url="https://anthropic.com/news/claude-3-7-sonnet",
        normalized_title="introducing claude 3 7 sonnet",
        category="agentic_ai",
    )

    item2 = ScoredItem(
        raw_item=RawItem(
            source_name="TechCrunch",
            source_type="rss",
            title="Anthropic launches Claude 3.7 Sonnet with hybrid reasoning capabilities",
            content="TechCrunch coverage of Anthropic's new model launch.",
            link="https://techcrunch.com/2026/02/anthropic-claude-3-7/?utm_source=rss",
            priority="medium",
        ),
        score=35.0,
        canonical_url="https://techcrunch.com/2026/02/anthropic-claude-3-7",
        normalized_title="anthropic launches claude 3 7 sonnet with hybrid reasoning capabilities",
        category="models",
    )

    clusters = cluster_stories([item1, item2], similarity_threshold=0.45)
    assert len(clusters) == 1
    cluster = clusters[0]
    assert cluster.primary_item.raw_item.source_name == "Anthropic Official"
    assert len(cluster.alternative_items) == 1
    assert cluster.alternative_items[0].raw_item.source_name == "TechCrunch"
    assert len(cluster.all_sources) == 2
