"""End-to-end integration test of the digest pipeline."""

import os
from pathlib import Path
import pytest
from src.models import RawItem
from src.pipeline import run_digest_pipeline


def test_pipeline_dry_run(tmp_path, monkeypatch):
    state_file = tmp_path / "state.json"
    summaries_dir = tmp_path / "summaries"

    monkeypatch.setenv("NEWS_SUMMARY_STATE", str(state_file))
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("EMAIL_PROVIDER", "mock")
    monkeypatch.setenv("EMAIL_TO", "test@example.com")

    digest = run_digest_pipeline(
        digest_type="test",
        dry_run=True,
        output_dir=str(summaries_dir),
        force_mock_llm=True,
    )

    assert digest is not None
    assert digest.digest_type == "test"
    assert digest.timezone == "Asia/Kolkata"

    # Verify summaries directory was created and contains generated markdown files
    md_files = list(summaries_dir.glob("*.md"))
    assert len(md_files) > 0
