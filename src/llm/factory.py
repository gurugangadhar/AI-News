"""Factory for creating LLM providers."""

import os
from src.config import AppConfig
from src.llm.base import LLMProvider
from src.llm.claude import ClaudeProvider
from src.llm.gemini import GeminiProvider
from src.llm.mock import MockLLMProvider
from src.llm.openai_compat import OpenAICompatProvider


def get_llm_provider(config: AppConfig, force_mock: bool = False) -> LLMProvider:
    """Return configured LLM provider instance."""
    if force_mock:
        return MockLLMProvider(config)

    provider_name = (
        os.environ.get("LLM_PROVIDER") or config.llm_provider or "claude"
    ).lower().strip()

    if provider_name == "mock":
        return MockLLMProvider(config)

    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY") or config.llm_api_key
    openai_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("KIMI_API_KEY")

    # Explicit Gemini request OR Gemini key present if provider is default/claude and no anthropic key
    if provider_name in ("gemini", "google"):
        if gemini_key:
            return GeminiProvider(config)
        print("[WARNING] GEMINI_API_KEY not found. Falling back to MockLLMProvider.")
        return MockLLMProvider(config)

    # Check for Claude API key
    if provider_name in ("claude", "anthropic"):
        if anthropic_key:
            return ClaudeProvider(config)
        # Automatic key fallbacks
        if gemini_key:
            print("[INFO] ANTHROPIC_API_KEY not found; automatically using GEMINI_API_KEY.")
            return GeminiProvider(config)
        if openai_key:
            print("[INFO] ANTHROPIC_API_KEY not found; falling back to OpenAI/Kimi provider.")
            return OpenAICompatProvider(config)
        print("[WARNING] No LLM API key provided. Falling back to MockLLMProvider.")
        return MockLLMProvider(config)

    if provider_name in ("openai", "moonshot", "kimi", "openrouter", "deepseek"):
        if openai_key or config.llm_api_key:
            return OpenAICompatProvider(config)
        if gemini_key:
            print("[INFO] OpenAI key not found; automatically using GEMINI_API_KEY.")
            return GeminiProvider(config)
        print("[WARNING] No OpenAI/Kimi API key provided. Falling back to MockLLMProvider.")
        return MockLLMProvider(config)

    # General auto-detection if provider is unspecified
    if gemini_key:
        return GeminiProvider(config)
    if anthropic_key:
        return ClaudeProvider(config)
    if openai_key:
        return OpenAICompatProvider(config)

    return MockLLMProvider(config)
