"""Unit tests for relevance scoring and category classification."""

import pytest
from src.config import AppConfig
from src.models import RawItem
from src.scoring import classify_category, score_item


def test_classify_agentic_ai():
    item = RawItem(
        source_name="Test Source",
        source_type="rss",
        title="Building Multi-Agent Systems with MCP and Tool Calling",
        content="Guide to configuring autonomous agent loops using Model Context Protocol and LangGraph.",
    )
    cat = classify_category(item)
    assert cat == "agentic_ai"


def test_classify_ai_engineering():
    item = RawItem(
        source_name="Test Source",
        source_type="rss",
        title="Optimizing RAG Latency with vLLM and Hybrid Vector Search",
        content="Benchmarking chunk sizes, dense embeddings, and reranker throughput in production.",
    )
    cat = classify_category(item)
    assert cat == "ai_engineering"


def test_classify_microsoft_ai():
    item = RawItem(
        source_name="Test Source",
        source_type="rss",
        title="Azure AI Foundry Announces Agent Service Integration with Semantic Kernel",
        content="Enterprise developers can now orchestrate copilot agents across Azure AI Search.",
    )
    cat = classify_category(item)
    assert cat == "microsoft_ai"


def test_score_item_agent_boost():
    config = AppConfig()
    agent_item = RawItem(
        source_name="Anthropic Blog",
        source_type="rss",
        title="Announcing Model Context Protocol: The Open Standard for Agent Tool Integration",
        content="We release MCP enabling developers to connect agents to tools, databases, and APIs with structured outputs.",
        link="https://www.anthropic.com/news/model-context-protocol",
        priority="high",
    )
    scored = score_item(agent_item, config)
    assert scored.score >= 50.0
    assert scored.score_breakdown["source_quality"] >= 25.0
    assert scored.score_breakdown["technical_relevance"] >= 20.0


def test_score_item_clickbait_penalty():
    config = AppConfig()
    fluff_item = RawItem(
        source_name="Spam News",
        source_type="rss",
        title="This Insane New AI Tool Will Blow Your Mind - Coding Is Dead!",
        content="You won't believe what happens next as AI takes over everything in a revolutionary way.",
        priority="low",
    )
    scored = score_item(fluff_item, config)
    assert scored.score_breakdown["penalties"] > 0
    assert scored.score < 25.0
