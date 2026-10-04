"""Google Gemini LLM Provider implementation using native REST API."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import List

from src.config import AppConfig
from src.llm.base import LLMProvider
from src.llm.parser import fallback_digest_from_clusters, parse_digest_json
from src.llm.prompts import SYSTEM_PROMPT
from src.models import DigestContent, StoryCluster


class GeminiProvider(LLMProvider):
    """Summarizer using Google's Gemini API."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or config.llm_api_key
        )
        # Use gemini-1.5-flash or gemini-2.0-flash as default high-speed high-quality model
        self.model = os.environ.get("GEMINI_MODEL") or config.llm_model or "gemini-1.5-flash"
        if not self.model.startswith("gemini-"):
            self.model = "gemini-1.5-flash"

    def _call_gemini_api(self, prompt: str, system_prompt: str) -> str:
        """Call Google Gemini REST API with JSON mode enabled."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AIEngineerDigest/2.0",
        }
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
                "maxOutputTokens": 4096,
            }
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    candidates = res_body.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                    raise ValueError(f"Unexpected Gemini API response structure: {res_body}")
            except urllib.error.HTTPError as e:
                err_text = e.read().decode("utf-8", errors="replace")
                print(f"[Gemini API Error {e.code}] Attempt {attempt + 1}/3: {err_text}")
                if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(4 * (attempt + 1))
                    continue
                raise
            except Exception as e:
                print(f"[Gemini Network Error] Attempt {attempt + 1}/3: {e}")
                if attempt < 2:
                    time.sleep(4 * (attempt + 1))
                    continue
                raise

        raise RuntimeError("Failed to obtain response from Gemini API after 3 attempts.")

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
            print(f"[INFO] Invoking Gemini model '{self.model}' for {len(items_payload)} candidates...")
            raw_response = self._call_gemini_api(user_prompt, SYSTEM_PROMPT)
            return parse_digest_json(raw_response, digest_type, date_str, period_label, clusters)
        except Exception as e:
            print(f"[WARNING] Gemini summarization failed: {e}. Falling back to rule-based digest.")
            return fallback_digest_from_clusters(clusters, digest_type, date_str, period_label)
