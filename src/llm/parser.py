"""Parsing and validation of LLM outputs into structured DigestContent."""

import json
import re
from typing import Any, Dict, List, Optional
from src.models import DigestContent, ProjectIdea, StoryCluster, StorySummary


def clean_json_text(text: str) -> str:
    """Strip markdown code blocks and whitespace from JSON response."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def parse_story(item_dict: Dict[str, Any], default_cat: str = "ai_engineering") -> StorySummary:
    """Parse a single story dictionary safely."""
    alts = item_dict.get("alternative_sources", [])
    if not isinstance(alts, list):
        alts = []

    return StorySummary(
        title=item_dict.get("title", "Untitled Story"),
        what_happened=item_dict.get("what_happened", ""),
        why_it_matters=item_dict.get("why_it_matters", ""),
        developer_impact=item_dict.get("developer_impact", ""),
        practical_takeaway=item_dict.get("practical_takeaway", ""),
        primary_url=item_dict.get("primary_url", item_dict.get("url", "")),
        source_name=item_dict.get("source_name", "Official Source"),
        alternative_sources=alts,
        category=item_dict.get("category", default_cat),
        tags=item_dict.get("tags", []),
        is_updated=bool(item_dict.get("is_updated", False)),
    )


def parse_digest_json(
    raw_response: str,
    digest_type: str,
    date_str: str,
    period_label: str,
    clusters: List[StoryCluster],
) -> DigestContent:
    """Parse raw LLM JSON response into a DigestContent object."""
    cleaned = clean_json_text(raw_response)
    try:
        data = json.loads(cleaned)
    except Exception as e:
        print(f"[WARNING] JSON parsing failed: {e}. Attempting fallback extraction.")
        return fallback_digest_from_clusters(clusters, digest_type, date_str, period_label)

    # Top stories
    top_stories = [parse_story(s, "top") for s in data.get("top_stories", [])]

    # Categories
    agentic_ai = [parse_story(s, "agentic_ai") for s in data.get("agentic_ai", [])]
    models_llms = [parse_story(s, "models") for s in data.get("models_llms", [])]
    ai_engineering = [parse_story(s, "ai_engineering") for s in data.get("ai_engineering", [])]
    ai_tools = [parse_story(s, "ai_coding") for s in data.get("ai_tools", [])]
    cloud_ai = [parse_story(s, "microsoft_ai") for s in data.get("cloud_ai", [])]
    github_oss = [parse_story(s, "github_oss") for s in data.get("github_oss", [])]
    research = [parse_story(s, "research") for s in data.get("research", [])]

    # Actionable learning & project idea
    what_to_learn = [str(x) for x in data.get("what_to_learn", []) if str(x).strip()]
    raw_proj = data.get("project_idea")
    project_idea = None
    if isinstance(raw_proj, dict) and raw_proj.get("title") and raw_proj.get("description"):
        project_idea = ProjectIdea(
            title=raw_proj.get("title", ""),
            description=raw_proj.get("description", ""),
            technologies=raw_proj.get("technologies", ["Python"]),
            difficulty=raw_proj.get("difficulty", "Intermediate"),
            portfolio_value=raw_proj.get("portfolio_value", ""),
        )

    career_signals = [str(x) for x in data.get("career_signals", []) if str(x).strip()]
    quick_links = data.get("quick_links", [])
    if not isinstance(quick_links, list):
        quick_links = []

    total_stories = (
        len(top_stories) + len(agentic_ai) + len(models_llms)
        + len(ai_engineering) + len(ai_tools) + len(cloud_ai)
        + len(github_oss) + len(research)
    )
    is_quiet = total_stories < 2

    return DigestContent(
        digest_type=digest_type,
        date_display=date_str,
        period_label=period_label,
        top_stories=top_stories,
        agentic_ai=agentic_ai,
        models_llms=models_llms,
        ai_engineering=ai_engineering,
        ai_tools=ai_tools,
        cloud_ai=cloud_ai,
        github_oss=github_oss,
        research=research,
        what_to_learn=what_to_learn,
        project_idea=project_idea,
        career_signals=career_signals,
        quick_links=quick_links,
        is_quiet_window=is_quiet,
        stats={"total_stories": total_stories, "clusters_considered": len(clusters)},
    )


def fallback_digest_from_clusters(
    clusters: List[StoryCluster],
    digest_type: str,
    date_str: str,
    period_label: str,
) -> DigestContent:
    """Generate a deterministic fallback digest directly from clusters if LLM fails."""
    top_stories = []
    agentic_ai = []
    models_llms = []
    ai_eng = []
    ai_tools = []
    cloud_ai = []
    github_oss = []
    research = []

    for idx, c in enumerate(clusters[:15]):
        cat = c.category
        summary = StorySummary(
            title=c.title,
            what_happened=c.primary_item.raw_item.content[:240] + ("..." if len(c.primary_item.raw_item.content) > 240 else ""),
            why_it_matters=f"Significant technical announcement from {c.source_name}.",
            developer_impact="Examine official documentation and API updates for implementation details.",
            practical_takeaway=f"Review source documentation at {c.link or 'official feed'}.",
            primary_url=c.link or "",
            source_name=c.source_name,
            alternative_sources=c.all_sources[1:],
            category=cat,
        )

        if idx < 5:
            top_stories.append(summary)
        elif cat == "agentic_ai":
            agentic_ai.append(summary)
        elif cat == "models":
            models_llms.append(summary)
        elif cat == "ai_engineering":
            ai_eng.append(summary)
        elif cat == "ai_coding":
            ai_tools.append(summary)
        elif cat in ("microsoft_ai", "google_ai"):
            cloud_ai.append(summary)
        elif cat == "github_oss":
            github_oss.append(summary)
        elif cat == "research":
            research.append(summary)
        else:
            ai_eng.append(summary)

    what_to_learn = [
        "Review official documentation for today's top technical releases",
        "Test tool calling and agent orchestration patterns against new model endpoints",
        "Benchmark RAG retrieval accuracy and chunking strategies with current toolsets"
    ]

    career_signals = [
        "High demand for production-grade Agent orchestration and MCP interoperability",
        "Continued enterprise shift toward evaluation-driven LLM application engineering"
    ]

    return DigestContent(
        digest_type=digest_type,
        date_display=date_str,
        period_label=period_label,
        top_stories=top_stories,
        agentic_ai=agentic_ai,
        models_llms=models_llms,
        ai_engineering=ai_eng,
        ai_tools=ai_tools,
        cloud_ai=cloud_ai,
        github_oss=github_oss,
        research=research,
        what_to_learn=what_to_learn,
        project_idea=None,
        career_signals=career_signals,
        quick_links=[],
        is_quiet_window=len(clusters) == 0,
        stats={"total_stories": len(top_stories) + len(agentic_ai) + len(ai_eng), "clusters_considered": len(clusters)},
    )
