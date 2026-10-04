"""Unit tests for configuration loading and validation."""

import os
import pytest
from src.config import load_app_config


def test_load_default_config():
    cfg = load_app_config()
    assert cfg.timezone == "Asia/Kolkata"
    assert "AI Engineer" in cfg.role_targets
    assert "AI Agents" in cfg.priority_topics
    assert cfg.max_total_stories >= 10
    assert len(cfg.sources) > 0


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("TIMEZONE", "Asia/Kolkata")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o")
    monkeypatch.setenv("EMAIL_PROVIDER", "resend")
    monkeypatch.setenv("EMAIL_TO", "engineer@example.com")

    cfg = load_app_config()
    assert cfg.timezone == "Asia/Kolkata"
    assert cfg.llm_provider == "openai"
    assert cfg.llm_model == "gpt-4o"
    assert cfg.email_provider == "resend"
    assert cfg.email_to == "engineer@example.com"
