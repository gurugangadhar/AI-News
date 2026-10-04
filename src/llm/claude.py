"""Anthropic Claude LLM Provider implementation."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from src.config import AppConfig
from src.llm.base import LLMProvider
from src.llm.parser import fallback_digest_from_clusters, parse_digest_json
from src.llm.prompts import SYSTEM_PROMPT
from src.models import DigestContent, StoryCluster


class ClaudeProvider(LLMProvider):
    """Summarizer using Anthropic's Claude API."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.api_key = config.llm_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = config.llm_model or "claude-3-5-sonnet-20241022"

    def _call_anthropic_api(self, prompt: str, system_prompt: str) -> str:
        """Call Anthropic API via SDK or fallback to urllib."""
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set.")

        # Try anthropic package first if installed
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except ImportError:
            pass

        # Fallback to direct HTTPS request via urllib
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "User-Agent": "AIEngineerDigest/2.0",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4000,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}]
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    content_blocks = res_body.get("content", [])
                    if content_blocks and "text" in content_blocks[0]:
                        return content_blocks[0]["text"]
                    raise ValueError(f"Unexpected response structure: {res_body}")
            except urllib.error.HTTPError as e:
                err_text = e.read().decode("utf-8", errors="replace")
                print(f"[Claude API error {e.code}] Attempt {attempt + 1}/3: {err_text}")
                if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
            except Exception as e:
                print(f"[Claude API error] Attempt {attempt + 1}/3: {e}")
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise

        raise RuntimeError("Failed to obtain response from Claude API after 3 attempts.")

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

        if not clusters:
            return fallback_digest_from_clusters(clusters, digest_type, date_str, period_label)

        # Prepare payload for LLM
        items_payload = []
        for idx, c in enumerate(clusters[:20]):
            items_payload.append({
                "id": idx + 1,
                "title": c.title,
                "source": c.source_name,
                "category": c.category,
                "link": c.link,
                "content": c.primary_item.raw_item.content[:1500],
                "alternative_sources": c.all_sources[1:],
                "importance_score": c.importance_score,
            })

        user_prompt = f"""Generate the Personal AI Engineer Daily Digest for {date_str} ({period_label}).

TARGET ROLES:
{', '.join(role_targets)}

PRIORITY DOMAINS:
{', '.join(priority_topics)}

CANDIDATE STORIES:
{json.dumps(items_payload, ensure_ascii=False, indent=2)}

Please analyze, synthesize, and return the complete JSON digest as requested.
"""

        try:
            print(f"[INFO] Invoking Claude model '{self.model}' for {len(items_payload)} candidates...")
            raw_response = self._call_anthropic_api(user_prompt, SYSTEM_PROMPT)
            return parse_digest_json(raw_response, digest_type, date_str, period_label, clusters)
        except Exception as e:
            print(f"[WARNING] Claude summarization failed: {e}. Falling back to rule-based digest.")
            return fallback_digest_from_clusters(clusters, digest_type, date_str, period_label)
