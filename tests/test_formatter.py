"""Unit tests for HTML email and Markdown generation."""

import pytest
from src.formatter import build_html_email, build_markdown_digest
from src.models import DigestContent, ProjectIdea, StorySummary


def test_build_html_and_markdown():
    story1 = StorySummary(
        title="Anthropic Launches Claude 3.7 Sonnet",
        what_happened="Anthropic announced Claude 3.7 Sonnet with hybrid reasoning capabilities.",
        why_it_matters="Allows dynamic allocation of reasoning tokens in agent tool loops.",
        developer_impact="Requires updating tool calling timeouts and handling reasoning tokens.",
        practical_takeaway="Test Claude 3.7 Sonnet on complex coding and agent benchmarks.",
        primary_url="https://www.anthropic.com/news/claude-3-7-sonnet",
        source_name="Anthropic Official",
        category="agentic_ai",
    )

    digest = DigestContent(
        digest_type="morning",
        date_display="06 October 2026",
        period_label="Morning Briefing",
        timezone="Asia/Kolkata",
        top_stories=[story1],
        what_to_learn=["Learn MCP stdio and SSE transport mechanisms"],
        project_idea=ProjectIdea(
            title="MCP Tool Gateway",
            description="Production reverse proxy for agent tool execution.",
            technologies=["Python", "FastAPI"],
            difficulty="Intermediate",
            portfolio_value="High value for enterprise agent roles",
        ),
        career_signals=["Growing enterprise demand for agent observability"],
    )

    # HTML verification
    html_out = build_html_email(digest)
    assert "<!DOCTYPE html>" in html_out
    assert "AI ENGINEER DAILY DIGEST" in html_out
    assert "Claude 3.7 Sonnet" in html_out
    assert "https://www.anthropic.com/news/claude-3-7-sonnet" in html_out
    assert "WHAT TO LEARN TODAY" in html_out
    assert "MCP Tool Gateway" in html_out
    assert "CAREER SIGNAL" in html_out

    # Markdown verification
    md_out = build_markdown_digest(digest)
    assert "# AI Engineer Daily Digest — Morning Briefing" in md_out
    assert "Claude 3.7 Sonnet" in md_out
    assert "What to Learn Today" in md_out
    assert "Project Idea" in md_out
