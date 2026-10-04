"""Core pipeline orchestrator for Personal AI Engineer Daily Digest.

Pipeline:
COLLECT -> FILTER -> DEDUPLICATE -> CLASSIFY -> SUMMARIZE -> RANK -> FORMAT -> EMAIL
"""

from datetime import datetime
import os
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple

from src import state as _state
from src.config import AppConfig, SourceConfig, load_app_config
from src.dedup import cluster_stories
from src.email import get_email_sender
from src.fetchers import (
    RawItem,
    fetch_email,
    fetch_follow_builders_podcasts,
    fetch_follow_builders_x,
    fetch_github_trending,
    fetch_gmail,
    fetch_hf_papers,
    fetch_rss,
    fetch_twitter,
    fetch_youtube,
    fetch_youtube_transcript,
)
from src.formatter import build_html_email, build_markdown_digest
from src.llm import get_llm_provider
from src.models import DigestContent, ScoredItem, StoryCluster
from src.scoring import score_item


def collect_raw_items(sources: List[SourceConfig], max_age_days: int = 7) -> List[RawItem]:
    """Phase 1: COLLECT raw items from all enabled sources."""
    items: List[RawItem] = []
    print(f"[INFO] Collecting from {len(sources)} configured sources...")

    for src in sources:
        if not src.enabled:
            continue

        stype = src.type.lower()
        name = src.name
        cat = src.category
        priority = src.priority
        before_count = len(items)

        try:
            if stype == "rss":
                if src.url:
                    res = fetch_rss(
                        url=src.url,
                        source_name=name,
                        max_entries=src.max_entries,
                        fetch_fulltext=src.fetch_fulltext,
                        fulltext_chars=src.fulltext_chars,
                        max_age_days=max_age_days,
                        category=cat,
                        priority=priority,
                    )
                    items.extend(res)

            elif stype == "github_trending":
                res = fetch_github_trending(
                    url=src.url,
                    source_name=name,
                    max_entries=src.max_entries,
                    category=cat,
                    priority=priority,
                )
                items.extend(res)

            elif stype == "hf_papers":
                res = fetch_hf_papers(
                    url=src.url,
                    source_name=name,
                    max_entries=src.max_entries,
                    category=cat,
                    priority=priority,
                )
                items.extend(res)

            elif stype == "follow_builders_x":
                res = fetch_follow_builders_x(
                    max_tweets_per_person=src.extra.get("max_tweets_per_person", 2)
                )
                for r in res:
                    r.category = "agentic_ai"
                    r.priority = priority
                items.extend(res)

            elif stype == "follow_builders_podcasts":
                res = fetch_follow_builders_podcasts(
                    max_episodes=src.extra.get("max_episodes", 2),
                    transcript_chars=src.extra.get("transcript_chars", 5000),
                )
                for r in res:
                    r.category = "agentic_ai"
                    r.priority = priority
                items.extend(res)

            elif stype == "youtube":
                if src.url:
                    items.extend(fetch_youtube(src.url, name, max_entries=src.max_entries))

            elif stype == "youtube_transcript":
                items.extend(fetch_youtube_transcript(
                    source_name=name,
                    channel_handle=src.extra.get("channel_handle"),
                    playlist_id=src.extra.get("playlist_id"),
                    lookback_hours=src.extra.get("lookback_hours", 72),
                ))

            elif stype == "twitter":
                cookies_path = src.extra.get("cookies_path") or os.environ.get("TWITTER_COOKIES_PATH", "twitter_cookies.json")
                items.extend(fetch_twitter(
                    cookies_path=cookies_path,
                    source_name=name,
                    usernames=src.extra.get("usernames", []),
                    max_tweets=src.extra.get("max_tweets", 10),
                ))

            elif stype == "email":
                if all(src.extra.get(k) for k in ("imap_server", "email", "password")):
                    items.extend(fetch_email(
                        imap_server=src.extra["imap_server"],
                        email=src.extra["email"],
                        password=src.extra["password"],
                        source_name=name,
                        folder=src.extra.get("folder", "INBOX"),
                        search_from=src.extra.get("search_from"),
                        max_emails=src.max_entries,
                    ))

            elif stype == "gmail":
                items.extend(fetch_gmail(
                    source_name=name,
                    credentials_json=src.extra.get("credentials_json"),
                    query=src.extra.get("query", "is:unread"),
                    max_emails=src.max_entries,
                ))

        except Exception as e:
            print(f"[WARNING] Error fetching from '{name}' ({stype}): {e}")

        added = len(items) - before_count
        if added > 0:
            print(f"  [+] {name}: {added} items")

    print(f"[INFO] Phase 1 COLLECT complete: {len(items)} items.")
    return items


def filter_and_score_items(
    items: List[RawItem],
    config: AppConfig,
    state_data: dict,
    digest_type: str,
    ignore_state: bool = False,
) -> List[ScoredItem]:
    """Phase 2 & 3: FILTER low quality / already sent items and SCORE relevance."""
    scored_items: List[ScoredItem] = []
    max_age_hours = config.max_age_hours_test if digest_type == "test" else config.max_age_hours_regular

    for item in items:
        # Ignore error placeholders
        if item.title.startswith("[") and item.title.endswith("]"):
            continue
        if len(item.content.strip()) < 20 and len(item.title.strip()) < 15:
            continue

        # Check if already sent recently in state (unless test mode or ignore_state)
        if not ignore_state and digest_type != "test":
            if _state.is_story_already_sent(
                state=state_data,
                url=item.link,
                title=item.title,
                max_age_hours=max_age_hours,
            ):
                continue

        # Score item
        scored = score_item(item, config)
        scored_items.append(scored)

    print(f"[INFO] Phase 2 & 3 FILTER & SCORE complete: {len(scored_items)} surviving scored items.")
    return scored_items


def rank_and_select_clusters(
    clusters: List[StoryCluster],
    config: AppConfig,
) -> List[StoryCluster]:
    """Phase 5: RANK and select top candidates for final briefing."""
    if not clusters:
        return []

    # Sort descending by importance score
    sorted_clusters = sorted(clusters, key=lambda c: c.importance_score, reverse=True)

    # Reserve Top 5
    selected: List[StoryCluster] = sorted_clusters[:config.top_stories_count]
    selected_links = {c.primary_item.raw_item.link for c in selected}

    # Category buckets to ensure broad balance
    category_counts: Dict[str, int] = {}
    for c in selected:
        category_counts[c.category] = category_counts.get(c.category, 0) + 1

    for c in sorted_clusters[config.top_stories_count:]:
        if len(selected) >= config.max_total_stories:
            break
        cat = c.category
        curr_count = category_counts.get(cat, 0)
        if curr_count < config.max_per_category:
            selected.append(c)
            selected_links.add(c.primary_item.raw_item.link)
            category_counts[cat] = curr_count + 1

    print(f"[INFO] Phase 5 RANK & SELECT complete: {len(selected)} clusters chosen for LLM synthesis.")
    return selected


def run_digest_pipeline(
    digest_type: str = "morning",
    dry_run: bool = False,
    config_path: Optional[str] = None,
    sources_path: Optional[str] = None,
    output_dir: str = "summaries",
    force_mock_llm: bool = False,
) -> DigestContent:
    """Execute complete end-to-end digest pipeline."""
    print("=" * 60)
    print(f"Personal AI Engineer Daily Digest — [{digest_type.upper()}] (Dry Run: {dry_run})")
    print("=" * 60)

    # 1. Load config
    config = load_app_config(config_path, sources_path)
    state_data = _state.load()

    # 2. Collect
    max_age_days = 7 if digest_type == "test" else 2
    raw_items = collect_raw_items(config.sources, max_age_days=max_age_days)

    # 3. Filter & Score
    scored_items = filter_and_score_items(
        items=raw_items,
        config=config,
        state_data=state_data,
        digest_type=digest_type,
        ignore_state=(digest_type == "test"),
    )

    # 4. Deduplicate & Cluster
    clusters = cluster_stories(scored_items, similarity_threshold=0.55)
    print(f"[INFO] Phase 4 DEDUPLICATE complete: clustered into {len(clusters)} unique events.")

    # 5. Rank & Select
    selected_clusters = rank_and_select_clusters(clusters, config)

    # 6. Summarize (LLM)
    llm = get_llm_provider(config, force_mock=force_mock_llm)
    now = datetime.now()
    date_display = now.strftime("%d %B %Y")

    print(f"[INFO] Phase 6 SUMMARIZE: Generating senior briefing with {llm.__class__.__name__}...")
    digest = llm.summarize_digest(
        clusters=selected_clusters,
        digest_type=digest_type,
        date_str=date_display,
        role_targets=config.role_targets,
        priority_topics=config.priority_topics,
    )
    digest.timezone = config.timezone
    digest.generated_at = now.isoformat()

    # 7. Format
    html_output = build_html_email(digest)
    md_output = build_markdown_digest(digest)

    # Save markdown archive
    out_dir_path = Path(output_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)
    today_str = now.strftime("%Y-%m-%d")

    # Save type-specific file and date file
    type_file = out_dir_path / f"{today_str}-{digest_type}.md"
    type_file.write_text(md_output, encoding="utf-8")
    print(f"[INFO] Saved Markdown digest: {type_file}")

    # Backward compatibility: also save YYYY-MM-DD.md
    base_file = out_dir_path / f"{today_str}.md"
    base_file.write_text(md_output, encoding="utf-8")

    # 8. Deliver Email
    sender = get_email_sender(config, dry_run=dry_run)
    period_label = "Morning" if digest_type == "morning" else "Evening" if digest_type == "evening" else "TEST"

    if digest_type == "test":
        subject = f"[TEST] AI Engineer Daily Digest — {date_display}"
    else:
        subject = f"AI Engineer Daily Digest — {period_label} — {date_display}"

    recipients = [r.strip() for r in config.email_to.split(",") if r.strip()]
    if not recipients and (config.smtp_user or os.environ.get("EMAIL_USER")):
        recipients = [config.smtp_user or os.environ.get("EMAIL_USER")]

    print(f"[INFO] Phase 8 DELIVER: Sending to {recipients or ['(dry-run / preview)']} via {sender.__class__.__name__}...")
    send_success = sender.send(
        subject=subject,
        html_content=html_output,
        text_content=md_output,
        recipients=recipients,
        from_address=config.email_from,
    )

    # 9. Record Sent State
    if send_success and not dry_run and digest_type != "test":
        for s in digest.top_stories + digest.agentic_ai + digest.models_llms + digest.ai_engineering:
            _state.record_story_sent(
                state=state_data,
                url=s.primary_url,
                title=s.title,
                digest_type=digest_type,
            )
        _state.save(state_data)
        print("[INFO] Successfully recorded sent stories to state.json.")

    print(f"[SUCCESS] Pipeline complete for {digest_type} run.")
    return digest
