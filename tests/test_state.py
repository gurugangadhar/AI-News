"""Unit tests for deduplication state management."""

import json
import os
import time
from pathlib import Path
import pytest
from src import state as _state


def test_normalize_title():
    t = "OpenAI Announces GPT-4o: Omni Multimodal Model - OpenAI Blog"
    norm = _state.normalize_title(t)
    assert "openai" in norm
    assert "gpt 4o" in norm


def test_is_story_already_sent(tmp_path, monkeypatch):
    state_file = tmp_path / "state.json"
    monkeypatch.setenv("NEWS_SUMMARY_STATE", str(state_file))

    st = _state.load()
    url = "https://example.com/ai-update-1"
    title = "Major Breakthrough in Agent Architectures"

    # Initially not sent
    assert not _state.is_story_already_sent(st, url=url, title=title)

    # Record as sent
    _state.record_story_sent(st, url=url, title=title, digest_type="morning")
    _state.save(st)

    # Reload state
    st_loaded = _state.load()
    assert _state.is_story_already_sent(st_loaded, url=url)
    assert _state.is_story_already_sent(st_loaded, title=title)
    assert _state.is_story_already_sent(st_loaded, title="Major Breakthrough in Agent Architectures - Tech News")


def test_state_retention_cleanup(tmp_path, monkeypatch):
    state_file = tmp_path / "state.json"
    monkeypatch.setenv("NEWS_SUMMARY_STATE", str(state_file))

    st = _state.load()
    # Add an expired entry (older than 10 seconds for test)
    old_time = time.time() - 200
    st["sentStories"]["https://old.com/article"] = {"last_sent": old_time}
    st["sentStories"]["https://new.com/article"] = {"last_sent": time.time()}

    _state.save(st, retention_seconds=100)
    st_reloaded = _state.load()

    assert "https://new.com/article" in st_reloaded["sentStories"]
    assert "https://old.com/article" not in st_reloaded["sentStories"]
