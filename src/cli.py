"""Command-line interface for Personal AI Engineer Daily Digest."""

import argparse
from datetime import datetime, timezone
import os
import sys

from src.pipeline import run_digest_pipeline


def detect_digest_type() -> str:
    """Detect morning vs evening based on environment variable or current UTC hour."""
    env_type = os.environ.get("DIGEST_TYPE", "").lower().strip()
    if env_type in ("morning", "evening", "test"):
        return env_type

    # Default schedule:
    # Morning: 06:00 IST = 00:30 UTC
    # Evening: 18:00 IST = 12:30 UTC
    # Check current UTC hour:
    # 20:00 - 08:00 UTC -> morning run
    # 08:00 - 20:00 UTC -> evening run
    utc_hour = datetime.now(timezone.utc).hour
    if 21 <= utc_hour or utc_hour < 9:
        return "morning"
    else:
        return "evening"


def main():
    parser = argparse.ArgumentParser(
        description="Personal AI Engineer Daily Digest Generator"
    )
    parser.add_argument(
        "--type",
        choices=["morning", "evening", "test", "auto"],
        default="auto",
        help="Type of digest to run (default: auto detect based on schedule/time)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate run without sending live emails (saves preview HTML)",
    )
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="Use deterministic mock LLM for testing without API keys",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--sources",
        default=None,
        help="Path to sources.yaml",
    )
    parser.add_argument(
        "--output-dir",
        default="summaries",
        help="Directory to save markdown summaries",
    )

    args = parser.parse_args()

    digest_type = args.type
    if digest_type == "auto":
        digest_type = detect_digest_type()

    print(f"[START] Running AI Engineer Digest CLI (Type: {digest_type}, Dry Run: {args.dry_run})")

    try:
        run_digest_pipeline(
            digest_type=digest_type,
            dry_run=args.dry_run,
            config_path=args.config,
            sources_path=args.sources,
            output_dir=args.output_dir,
            force_mock_llm=args.mock_llm,
        )
    except Exception as e:
        print(f"[FATAL] Digest pipeline encountered an error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
