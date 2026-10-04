"""OpenAI-compatible LLM Provider (supports OpenAI, Moonshot/Kimi, OpenRouter, DeepSeek)."""

import json
import os
import time
from typing import List

from src.config import AppConfig
from src.llm.base import LLMProvider
from src.llm.parser import fallback_digest_from_clusters, parse_digest_json
from src.llm.prompts import SYSTEM_PROMPT
from src.models import DigestContent, StoryCluster


class OpenAICompatProvider(LLMProvider):
    """Summarizer using OpenAI-compatible APIs."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.api_key = config.llm_api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("KIMI_API_KEY")

        # Determine base_url
        if os.environ.get("OPENAI_BASE_URL"):
            self.base_url = os.environ.get("OPENAI_BASE_URL")
        elif "moonshot" in config.llm_model.lower() or os.environ.get("KIMI_API_KEY"):
            self.base_url = "https://api.moonshot.cn/v1"
        else:
            self.base_url = "https://api.openai.com/v1"

        self.model = config.llm_model or ("moonshot-v1-128k" if "moonshot" in self.base_url else "gpt-4o-mini")

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
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            print(f"[INFO] Invoking OpenAI-compat model '{self.model}' at '{self.base_url}'...")
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=4000,
            )
            raw_text = resp.choices[0].message.content or "{}"
            return parse_digest_json(raw_text, digest_type, date_str, period_label, clusters)
        except Exception as e:
            print(f"[WARNING] OpenAI-compat summarization failed: {e}. Falling back to rule-based digest.")
            return fallback_digest_from_clusters(clusters, digest_type, date_str, period_label)
