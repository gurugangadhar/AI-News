"""Deterministic Mock LLM Provider for unit testing and offline verification."""

from typing import List

from src.config import AppConfig
from src.llm.base import LLMProvider
from src.llm.parser import fallback_digest_from_clusters
from src.models import DigestContent, ProjectIdea, StoryCluster, StorySummary


class MockLLMProvider(LLMProvider):
    """Generates realistic structured responses without making external API calls."""

    def __init__(self, config: AppConfig):
        self.config = config

    def summarize_digest(
        self,
        clusters: List[StoryCluster],
        digest_type: str,
        date_str: str,
        role_targets: List[str],
        priority_topics: List[str],
    ) -> DigestContent:
        period_label = (
            "Morning Briefing" if digest_type == "morning"
            else "Evening Briefing" if digest_type == "evening"
            else "Test Verification Briefing"
        )

        base = fallback_digest_from_clusters(clusters, digest_type, date_str, period_label)

        # Enhance with simulated project idea and career signals
        base.project_idea = ProjectIdea(
            title="Multi-Agent Tool Orchestrator with MCP and Observability",
            description="Build a production-grade agent loop using Model Context Protocol (MCP) tool servers, integrating structured JSON schemas and latency tracing with OpenTelemetry.",
            technologies=["Python", "FastAPI", "LangGraph", "MCP SDK", "Docker"],
            difficulty="Intermediate",
            portfolio_value="Demonstrates end-to-end mastery of agentic architecture, tool execution protocols, and production observability.",
        )

        base.what_to_learn = [
            "Master Model Context Protocol (MCP) server architecture: stdio vs SSE transports",
            "Implement structured JSON output validation using Pydantic V2 and instructor",
            "Benchmark RAG chunking strategies and hybrid BM25 + dense vector retrieval",
            "Explore multi-agent delegation patterns with state machines and checkpointing"
        ]

        base.career_signals = [
            "Accelerating industry demand for Agentic AI Engineers skilled in MCP and tool-calling protocols",
            "Transition from naive prompt engineering to rigorous evaluation-driven LLM application development",
            "Enterprise preference for multi-agent orchestration frameworks (LangGraph, Semantic Kernel, AutoGen)"
        ]

        return base
