"""Multi-factor relevance scoring and classification engine for AI Engineers."""

import re
from typing import Dict, List, Tuple
from src.config import AppConfig
from src.dedup import canonicalize_url
from src.models import RawItem, ScoredItem
from src.state import compute_content_hash, normalize_title


# Categorization keywords
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "agentic_ai": [
        "agent", "agentic", "multi-agent", "autogen", "crewai", "langgraph",
        "semantic kernel", "mcp", "model context protocol", "a2a", "tool calling",
        "tool-use", "autonomous workflow", "subagent", "agent memory", "agent evaluation",
        "orchestration", "agent framework", "agentic workflow", "agentic ai"
    ],
    "ai_engineering": [
        "rag", "vector database", "embedding", "embeddings", "inference", "vllm",
        "ollama", "model serving", "evaluation", "observability", "structured output",
        "structured outputs", "function calling", "prompt engineering", "context engineering",
        "ai infrastructure", "fine-tuning", "lora", "triton", "quantization", "gguf",
        "retrieval", "rerank", "reranker", "latency", "token throughput", "langchain", "llamaindex"
    ],
    "ai_coding": [
        "claude code", "cursor", "windsurf", "github copilot", "codex", "coding agent",
        "autonomous coding", "software engineering agent", "swe-bench", "ai ide",
        "code generation", "code assist", "devin"
    ],
    "microsoft_ai": [
        "microsoft foundry", "azure ai", "azure openai", "copilot studio",
        "azure ai agent service", "microsoft agent framework", "semantic kernel",
        "azure ai search", "microsoft 365 ai", "azure machine learning"
    ],
    "google_ai": [
        "gemini", "gemini api", "google ai studio", "vertex ai",
        "vertex ai agent builder", "google adk", "agent development kit",
        "agent engine", "firebase ai", "deepmind", "imagen", "veo"
    ],
    "models": [
        "llm", "llms", "multimodal", "reasoning model", "open-source model",
        "model release", "benchmark", "weights", "llama", "deepseek", "mistral",
        "gpt-4", "gpt-5", "claude 3", "grok", "gemini 1.5", "gemini 2", "qwen"
    ],
    "github_oss": [
        "github", "open source", "repository", "open-source", "framework",
        "developer tools", "sdk", "python library", "cli"
    ],
    "research": [
        "arxiv", "paper", "research", "ablation", "state of the art", "sota",
        "attention mechanism", "transformer architecture", "scaling law", "alignment"
    ],
}

# High-value technical phrases that boost engineering score
ENGINEERING_BOOST_TERMS = [
    "production", "architecture", "evaluation", "benchmark", "mcp", "tool calling",
    "agent", "rag", "inference", "serving", "fine-tuning", "latency", "throughput",
    "optimization", "structured outputs", "api release", "open source", "sdk"
]

# Fluff / clickbait penalty terms
CLICKBAIT_TERMS = [
    "will blow your mind", "game-changing", "shocking", "insane", "unbelievable",
    "the end of coding", "you won't believe", "is dead", "revolutionize everything"
]


def classify_category(item: RawItem) -> str:
    """Classify item into one of the core categories."""
    # If category explicitly configured on source, check if valid
    if item.category and item.category in CATEGORY_KEYWORDS:
        return item.category

    text = f"{item.title} {item.content}".lower()

    # Score each category based on keyword density
    scores: Dict[str, int] = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in kws:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                # Title matches have double weight
                title_match = bool(re.search(r"\b" + re.escape(kw) + r"\b", item.title.lower()))
                score += 3 if title_match else 1
        scores[cat] = score

    # Agentic AI and AI Engineering priority bias
    scores["agentic_ai"] = int(scores.get("agentic_ai", 0) * 1.4)
    scores["ai_engineering"] = int(scores.get("ai_engineering", 0) * 1.2)

    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        return best_cat

    return item.category or "ai_engineering"


def score_item(item: RawItem, config: AppConfig) -> ScoredItem:
    """Compute multi-factor score for AI Engineer profile relevance."""
    text = f"{item.title} {item.content}".lower()
    title_lower = item.title.lower()

    # 1. Source Quality (0 - 25)
    source_quality = 15.0
    if item.priority == "high":
        source_quality = 25.0
    elif item.priority == "medium":
        source_quality = 18.0
    elif item.priority == "low":
        source_quality = 10.0

    # Official company blog bonus
    official_domains = ["openai.com", "anthropic.com", "deepmind.google", "microsoft.com", "meta.com", "huggingface.co"]
    if item.link and any(dom in item.link.lower() for dom in official_domains):
        source_quality = min(25.0, source_quality + 3.0)

    # 2. Technical Relevance (0 - 35)
    tech_score = 10.0
    category = classify_category(item)

    # Category weight bias
    if category == "agentic_ai":
        tech_score += 15.0
    elif category in ("ai_engineering", "ai_coding"):
        tech_score += 12.0
    elif category in ("microsoft_ai", "google_ai", "models"):
        tech_score += 10.0
    elif category in ("github_oss", "research"):
        tech_score += 8.0

    # Keyword boosts
    kw_count = 0
    for kw in config.priority_topics:
        if re.search(r"\b" + re.escape(kw.lower()) + r"\b", text):
            kw_count += 1
            if re.search(r"\b" + re.escape(kw.lower()) + r"\b", title_lower):
                tech_score += 3.0
            else:
                tech_score += 1.5
    tech_score = min(35.0, tech_score)

    # 3. Career Relevance (0 - 20)
    career_score = 5.0
    career_skills = [
        "python", "fastapi", "rag", "mcp", "langgraph", "semantic kernel",
        "google adk", "foundry", "vector database", "evaluation", "inference",
        "docker", "kubernetes", "llm api", "function calling", "tool use",
        "structured outputs", "agent memory", "agent orchestration"
    ]
    for skill in career_skills:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            career_score += 2.0
    career_score = min(20.0, career_score)

    # 4. Novelty / Launch Signal (0 - 10)
    novelty_score = 3.0
    novelty_terms = [
        "announcing", "releases", "released", "launching", "launches", "introducing",
        "v0.", "v1.", "v2.", "v3.", "v4.", "now available", "open sources", "open-sourced"
    ]
    for term in novelty_terms:
        if term in title_lower:
            novelty_score += 4.0
            break
        elif term in text:
            novelty_score += 2.0
            break
    novelty_score = min(10.0, novelty_score)

    # 5. Engineering Value / Hands-on (0 - 10)
    eng_score = 2.0
    for term in ENGINEERING_BOOST_TERMS:
        if term in text:
            eng_score += 1.0
    eng_score = min(10.0, eng_score)

    # Penalties
    penalties = 0.0
    for click in CLICKBAIT_TERMS:
        if click in text:
            penalties += 8.0

    # Corporate minor fluff penalty (finance, stock, board of directors, lawsuit)
    fluff_terms = ["shares rise", "stock jumps", "quarterly earnings", "board member", "sues", "lawsuit"]
    for fluff in fluff_terms:
        if fluff in text:
            penalties += 12.0

    total_score = max(5.0, (source_quality + tech_score + career_score + novelty_score + eng_score) - penalties)

    canonical_url = canonicalize_url(item.link or "")
    normalized_t = normalize_title(item.title)
    content_hash = compute_content_hash(f"{item.title} {item.content}")

    return ScoredItem(
        raw_item=item,
        score=round(total_score, 2),
        score_breakdown={
            "source_quality": round(source_quality, 1),
            "technical_relevance": round(tech_score, 1),
            "career_relevance": round(career_score, 1),
            "novelty": round(novelty_score, 1),
            "engineering_value": round(eng_score, 1),
            "penalties": round(penalties, 1),
        },
        canonical_url=canonical_url,
        normalized_title=normalized_t,
        content_hash=content_hash,
        category=category,
    )
