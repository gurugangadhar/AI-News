"""Configuration loader and management."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class SourceConfig:
    name: str
    type: str = "rss"
    url: Optional[str] = None
    category: str = "ai_engineering"
    priority: str = "medium"
    enabled: bool = True
    max_entries: int = 3
    fetch_fulltext: bool = False
    fulltext_chars: int = 8000
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppConfig:
    timezone: str = "Asia/Kolkata"
    morning_time: str = "06:00"
    evening_time: str = "18:00"
    role_targets: List[str] = field(default_factory=lambda: [
        "AI Engineer", "Generative AI Engineer", "AI Agent Developer",
        "Agentic AI Engineer", "AI Application Developer", "LLM Engineer"
    ])
    priority_topics: List[str] = field(default_factory=lambda: [
        "AI Agents", "Agentic AI", "Multi-Agent Systems", "MCP",
        "Tool Calling", "Function Calling", "RAG", "Vector Databases",
        "Inference", "Model Serving", "Evaluation", "Observability", "AI Coding"
    ])
    secondary_topics: List[str] = field(default_factory=lambda: [
        "Microsoft Foundry", "Azure AI", "Semantic Kernel", "Copilot Studio",
        "Google ADK", "Vertex AI", "Gemini API", "Reasoning Models", "Open Source AI"
    ])
    max_total_stories: int = 18
    top_stories_count: int = 5
    max_per_category: int = 4
    max_age_hours_regular: int = 18
    max_age_hours_test: int = 168
    min_stories_for_digest: int = 2

    # LLM settings
    llm_provider: str = "claude"
    llm_model: str = "claude-3-5-sonnet-20241022"
    llm_fast_model: str = "claude-3-5-haiku-20241022"
    llm_api_key: Optional[str] = None

    # Email settings
    email_provider: str = "resend"
    email_from: str = "onboarding@resend.dev"
    email_to: str = ""
    resend_api_key: Optional[str] = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # Sources
    sources: List[SourceConfig] = field(default_factory=list)


def _find_file(candidates: List[str]) -> Optional[Path]:
    for cand in candidates:
        p = Path(cand)
        if p.is_file():
            return p
    return None


def load_app_config(
    config_path: Optional[str] = None,
    sources_path: Optional[str] = None,
) -> AppConfig:
    """Load and merge application configuration from YAML files and environment variables."""

    # 1. Resolve config.yaml
    cfg_file = None
    if config_path:
        cfg_file = Path(config_path)
    else:
        cfg_file = _find_file([
            "config/config.yaml",
            "config.yaml",
            "sources.yaml",  # backward compatibility
        ])

    raw_cfg: Dict[str, Any] = {}
    if cfg_file and cfg_file.is_file():
        try:
            with open(cfg_file, encoding="utf-8") as f:
                raw_cfg = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[WARNING] Could not parse config file {cfg_file}: {e}")

    # 2. Resolve sources.yaml
    src_file = None
    if sources_path:
        src_file = Path(sources_path)
    else:
        src_file = _find_file([
            "config/sources.yaml",
            "sources.yaml",
            "sources.example.yaml",
        ])

    raw_sources: List[Dict[str, Any]] = []
    if src_file and src_file.is_file():
        try:
            with open(src_file, encoding="utf-8") as f:
                src_data = yaml.safe_load(f) or {}
                if isinstance(src_data, dict):
                    raw_sources = src_data.get("sources", [])
                elif isinstance(src_data, list):
                    raw_sources = src_data
        except Exception as e:
            print(f"[WARNING] Could not parse sources file {src_file}: {e}")

    # Fallback if sources were inside config.yaml
    if not raw_sources and "sources" in raw_cfg:
        raw_sources = raw_cfg.get("sources", [])

    # Build typed SourceConfig list
    sources_list: List[SourceConfig] = []
    for s in raw_sources:
        if not isinstance(s, dict):
            continue
        sc = SourceConfig(
            name=s.get("name", "Unnamed Source"),
            type=s.get("type", "rss"),
            url=s.get("url"),
            category=s.get("category", "ai_engineering"),
            priority=s.get("priority", "medium"),
            enabled=s.get("enabled", True),
            max_entries=s.get("max_entries", 3),
            fetch_fulltext=s.get("fetch_fulltext", False),
            fulltext_chars=s.get("fulltext_chars", 8000),
            extra={k: v for k, v in s.items() if k not in {
                "name", "type", "url", "category", "priority",
                "enabled", "max_entries", "fetch_fulltext", "fulltext_chars"
            }}
        )
        sources_list.append(sc)

    # 3. Build AppConfig with env var overrides
    profile = raw_cfg.get("profile", {})
    schedule = raw_cfg.get("schedule", {})
    limits = raw_cfg.get("limits", {})
    llm_cfg = raw_cfg.get("llm", {})
    email_cfg = raw_cfg.get("email", {})

    timezone = (
        os.environ.get("TIMEZONE")
        or os.environ.get("DIGEST_TIMEZONE")
        or schedule.get("timezone", "Asia/Kolkata")
    )
    morning_time = (
        os.environ.get("MORNING_DIGEST_TIME")
        or schedule.get("morning_digest_time", "06:00")
    )
    evening_time = (
        os.environ.get("EVENING_DIGEST_TIME")
        or schedule.get("evening_digest_time", "18:00")
    )

    llm_provider = (
        os.environ.get("LLM_PROVIDER")
        or llm_cfg.get("provider", "claude")
    ).lower()

    llm_model = (
        os.environ.get("LLM_MODEL")
        or llm_cfg.get("model", "claude-3-5-sonnet-20241022")
    )

    llm_api_key = (
        os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("LLM_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("KIMI_API_KEY")
    )

    email_provider = (
        os.environ.get("EMAIL_PROVIDER")
        or email_cfg.get("provider", "resend")
    ).lower()

    email_from = (
        os.environ.get("EMAIL_FROM")
        or email_cfg.get("from_address", "onboarding@resend.dev")
    )

    email_to = (
        os.environ.get("EMAIL_TO")
        or email_cfg.get("to_address", "")
    )

    resend_api_key = os.environ.get("RESEND_API_KEY")
    smtp_user = os.environ.get("EMAIL_USER") or os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("EMAIL_PASSWORD") or os.environ.get("SMTP_PASSWORD")
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))

    return AppConfig(
        timezone=timezone,
        morning_time=morning_time,
        evening_time=evening_time,
        role_targets=profile.get("role_target", [
            "AI Engineer", "Generative AI Engineer", "AI Agent Developer",
            "Agentic AI Engineer", "AI Application Developer", "LLM Engineer"
        ]),
        priority_topics=profile.get("priority_topics", [
            "AI Agents", "Agentic AI", "Multi-Agent Systems", "MCP",
            "Tool Calling", "Function Calling", "RAG", "Vector Databases",
            "Inference", "Model Serving", "Evaluation", "Observability", "AI Coding"
        ]),
        secondary_topics=profile.get("secondary_topics", [
            "Microsoft Foundry", "Azure AI", "Semantic Kernel", "Copilot Studio",
            "Google ADK", "Vertex AI", "Gemini API", "Reasoning Models", "Open Source AI"
        ]),
        max_total_stories=int(limits.get("max_total_stories", 18)),
        top_stories_count=int(limits.get("top_stories_count", 5)),
        max_per_category=int(limits.get("max_per_category", 4)),
        max_age_hours_regular=int(limits.get("max_age_hours_regular", 18)),
        max_age_hours_test=int(limits.get("max_age_hours_test", 168)),
        min_stories_for_digest=int(limits.get("min_stories_for_digest", 2)),
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_fast_model=llm_cfg.get("fast_model", "claude-3-5-haiku-20241022"),
        llm_api_key=llm_api_key,
        email_provider=email_provider,
        email_from=email_from,
        email_to=email_to,
        resend_api_key=resend_api_key,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        sources=sources_list,
    )
