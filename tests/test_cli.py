"""Unit tests for CLI schedule detection and argument handling."""

import os
from src.cli import detect_digest_type


def test_detect_digest_type_from_env(monkeypatch):
    monkeypatch.setenv("DIGEST_TYPE", "morning")
    assert detect_digest_type() == "morning"

    monkeypatch.setenv("DIGEST_TYPE", "evening")
    assert detect_digest_type() == "evening"

    monkeypatch.setenv("DIGEST_TYPE", "test")
    assert detect_digest_type() == "test"


def test_detect_digest_type_default():
    # If no env var set, returns either morning or evening based on UTC hour
    os.environ.pop("DIGEST_TYPE", None)
    dtype = detect_digest_type()
    assert dtype in ("morning", "evening")
