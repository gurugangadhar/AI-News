# 🚀 Personal AI Engineer Daily Digest

> An automated, production-grade AI intelligence system delivering personalized daily briefings twice every day directly to your inbox via GitHub Actions.

Designed specifically for engineers preparing for:
- **AI Engineer**
- **Generative AI Engineer**
- **AI Agent Developer**
- **Agentic AI Engineer**
- **AI Application Developer**
- **LLM Engineer**

---

## 📋 Table of Contents
1. [Core Features](#-core-features)
2. [System Architecture](#-system-architecture)
3. [Target Content & Categories](#-target-content--categories)
4. [Twice-Daily Schedule (IST ↔ UTC)](#-twice-daily-schedule-ist--utc)
5. [Briefing Structure & Email Format](#-briefing-structure--email-format)
6. [Source Management (`config/sources.yaml`)](#-source-management-configsourcesyaml)
7. [Deduplication & Multi-Factor Scoring](#-deduplication--multi-factor-scoring)
8. [GitHub Actions Setup & Secrets](#-github-actions-setup--secrets)
9. [Local Development & CLI Usage](#-local-development--cli-usage)
10. [Test Suite](#-test-suite)
11. [Troubleshooting & FAQ](#-troubleshooting--faq)

---

## ✨ Core Features

- **Senior AI Engineer Briefing Tone**: Direct, technical, and actionable. Zero marketing hype or buzzwords like "revolutionary" or "game-changing".
- **Highest Priority on Agentic AI & AI Engineering**: Focused on production tool-calling, multi-agent frameworks, MCP (Model Context Protocol), RAG retrieval, model serving, and evaluation.
- **Twice-Daily Execution**:
  - **Morning Briefing** (06:00 AM IST): Overnight global releases, research papers, and breaking model updates.
  - **Evening Briefing** (06:00 PM IST): Daytime architectural developments, tools, and developer implementations.
- **Stateful Deduplication**: Cross-source clustering prevents the same story from appearing multiple times or repeating between morning and evening runs.
- **Actionable Career Growth**:
  - 📚 **What to Learn Today**: 3–5 practical exercises turning announcements into hands-on skills.
  - 🚀 **Portfolio Project Idea**: Concrete application ideas with recommended tech stacks and hiring manager appeal.
  - 🎯 **Career Signal**: Skill radar identifying technologies gaining industry adoption.
- **100% Serverless**: Runs completely in GitHub Actions without needing a personal computer or local server active.
- **Flexible Providers**: Native support for **Claude 3.5 Sonnet** (preferred) or OpenAI-compatible models, and **Resend** or **Gmail SMTP** email delivery.

---

## 🏗️ System Architecture

The pipeline processes intelligence through eight deterministic stages:

```
┌─────────┐     ┌────────┐     ┌─────────────┐     ┌──────────┐
│ COLLECT │ ──> │ FILTER │ ──> │ DEDUPLICATE │ ──> │ CLASSIFY │
└─────────┘     └────────┘     └─────────────┘     └──────────┘
                                                        │
┌─────────┐     ┌────────┐     ┌─────────────┐          ▼
│  EMAIL  │ <── │ FORMAT │ <── │  SUMMARIZE  │ <── ┌──────────┐
│ DELIVER │     │ (HTML) │     │    (LLM)    │     │   RANK   │
└─────────┘     └────────┘     └─────────────┘     └──────────┘
```

1. **COLLECT**: Pulls from RSS feeds, GitHub Trending APIs, Hugging Face papers, and engineering blogs. Each source fails independently with zero pipeline crashes.
2. **FILTER**: Prunes stale items (18h limit for regular runs), stripping boilerplate, ads, and parsing errors.
3. **DEDUPLICATE**: Canonicalizes URLs (stripping UTM params/tracking) and measures title similarity using token Jaccard and n-gram overlap to cluster duplicate coverage into single events.
4. **CLASSIFY**: Tags items across core domains with special weighting on Agentic AI and AI Engineering.
5. **RANK**: Evaluates each candidate with a 5-factor scoring engine (Source Quality + Technical Relevance + Career Relevance + Novelty + Engineering Value) to select the top 10–18 stories.
6. **SUMMARIZE**: Prompts the LLM (Claude 3.5 Sonnet) to generate structured senior briefings, learning actions, project ideas, and career signals.
7. **FORMAT**: Builds responsive, mobile-optimized HTML email cards and archives Markdown summaries.
8. **EMAIL**: Delivers the digest via Resend API or SMTP, persisting sent story IDs to `data/state.json`.

---

## 🎯 Target Content & Categories

| Category | Primary Focus Areas |
| :--- | :--- |
| **🤖 Agentic AI** *(Highest)* | Autonomous agents, LangGraph, AutoGen, CrewAI, Semantic Kernel, Model Context Protocol (MCP), tool-use, multi-agent loops, agent memory & evaluation. |
| **💻 AI Engineering** *(Highest)* | RAG retrieval, vector databases, embeddings, vLLM, model serving, prompt & context engineering, structured JSON outputs, observability. |
| **🧠 Models & Generative AI** | Frontier LLMs (OpenAI, Anthropic, Google DeepMind, Meta, Mistral, DeepSeek), multimodal models, reasoning models, open weights, benchmarks. |
| **☁️ Microsoft AI** | Azure AI Foundry, Azure OpenAI, Semantic Kernel, Copilot Studio, Azure AI Agent Service, Azure AI Search. |
| **☁️ Google AI** | Gemini API, Google AI Studio, Vertex AI Agent Builder, Google ADK, Agent Engine, DeepMind research. |
| **🛠️ AI Tools & Coding** | Claude Code, Cursor, Windsurf, GitHub Copilot, coding agents, SWE-bench evaluations, developer CLIs. |
| **⭐ GitHub & Open Source** | Trending production repositories, open-source AI frameworks, developer SDKs, inference runtimes. |
| **🔬 Practical Research** | ArXiv and Hugging Face papers with direct engineering implications (inference acceleration, KV-cache optimization, agentic reasoning). |

---

## ⏰ Twice-Daily Schedule (IST ↔ UTC)

GitHub Actions triggers on UTC. The table below illustrates the standard schedule for `Asia/Kolkata` (IST, UTC+5:30):

| Run Type | Target Time (IST) | Scheduled Time (UTC) | GitHub Actions Cron Expression |
| :--- | :--- | :--- | :--- |
| **Morning Digest** | **06:00 AM IST** | **00:30 UTC** | `30 0 * * *` |
| **Evening Digest** | **06:00 PM IST** | **12:30 UTC** | `30 12 * * *` |

> [!NOTE]
> When manually triggering via the GitHub Actions UI (`workflow_dispatch`), select `auto` to let the workflow detect morning vs evening based on the current hour, or select `morning`, `evening`, or `test` explicitly.

---

## 📬 Briefing Structure & Email Format

Each digest email features:
- **Header**: Date, digest type (Morning / Evening), and timezone (`Asia/Kolkata`).
- **🔥 Top 5 Developments**: High-priority stories presented with:
  - **What happened**: 2–4 concise sentences.
  - **Why it matters**: Architectural and industry impact.
  - **Developer impact**: Actionable insights for AI Engineers and Agent Developers.
  - **Takeaway**: Exact tools, APIs, or docs to inspect.
  - **Original Source Links**: Direct link plus citations to alternative outlets.
- **Categorized Sections**: Deep-dives into Agentic AI, Models, AI Engineering, Cloud AI, Coding Tools, GitHub, and Research.
- **📚 What to Learn Today**: 3–5 concrete technical exercises.
- **🚀 Project Idea**: Portfolio architecture overview with difficulty rating, tech stack, and hiring manager value.
- **🎯 Career Signal**: In-demand skills reflected in current market developments.
- **⚡ Quick Links**: Fast reference list with source badges.

---

## ⚙️ Source Management (`config/sources.yaml`)

Sources are decoupled from application logic in [`config/sources.yaml`](file:///config/sources.yaml).

### Adding a New Source
Add an entry under the `sources` list:

```yaml
- name: "LangChain & LangGraph Blog"
  type: rss
  url: "https://blog.langchain.dev/rss/"
  category: agentic_ai     # agentic_ai | ai_engineering | models | microsoft_ai | google_ai | ai_coding | github_oss | research
  priority: high           # high | medium | low
  enabled: true
  max_entries: 3
  fetch_fulltext: true
```

Supported source types:
- `rss`: Standard RSS/Atom feeds (Substack, WordPress, company blogs).
- `github_trending`: GitHub Search API queries for newly trending AI repositories.
- `hf_papers`: Hugging Face Daily Papers API.
- `follow_builders_x`: Twitter feed for 25+ top AI builders via follow-builders.
- `follow_builders_podcasts`: AI podcast transcripts (Latent Space, No Priors, etc.).

---

## 🔍 Deduplication & Multi-Factor Scoring

### Deduplication
- **URL Canonicalization**: Strips query tracking (`utm_*`, `ref`, `fbclid`, fragments) and normalizes protocols.
- **Title Normalization**: Tokenizes titles, removes stop words and branding suffixes (`- OpenAI`, `| TechCrunch`).
- **Story Clustering**: Calculates Jaccard token similarity and character bigram overlap. If similarity $\ge 0.55$, reports are merged into a single event with the official source prioritized.
- **State Tracking**: `data/state.json` caches sent story URLs, titles, and content hashes with an automatic 14-day retention pruning.

### Relevance Scoring Formula
$$\text{Score} = (\text{Source Quality} + \text{Technical Relevance} + \text{Career Relevance} + \text{Novelty} + \text{Engineering Value}) - \text{Penalties}$$

- **Source Quality (0–25)**: High-priority official sources receive top score.
- **Technical Relevance (0–35)**: Heavy weighting for Agentic AI, MCP, tool calling, and RAG keywords.
- **Career Relevance (0–20)**: Matches target skills (FastAPI, Python, Docker, evaluation frameworks, vector DBs).
- **Novelty (0–10)**: Boost for new version releases (`v0.x`, `v1.x`), launches, and open-source announcements.
- **Engineering Value (0–10)**: Boost for benchmarks, architecture diagrams, latency metrics, and production guides.
- **Penalties**: Deducts points for clickbait ("game-changing", "will blow your mind") and non-technical corporate news (lawsuits, stock changes).

---

## 🔐 GitHub Actions Setup & Secrets

### 1. Push Repository to GitHub
Push this codebase to your GitHub repository (e.g., `your-username/ai-daily-digest`).

### 2. Configure Repository Secrets
Navigate to: **Settings → Secrets and variables → Actions → Secrets → New repository secret**

| Secret Name | Required? | Description |
| :--- | :--- | :--- |
| `ANTHROPIC_API_KEY` | **Recommended** | Anthropic API key (`sk-ant-...`) for Claude 3.5 Sonnet. |
| `OPENAI_API_KEY` | Optional | OpenAI API key (`sk-...`) if using OpenAI models. |
| `RESEND_API_KEY` | **Recommended** | Resend API key (`re_...`) for modern HTTP email sending. |
| `EMAIL_TO` | **Required** | Your personal email address where digests will be delivered. |
| `EMAIL_USER` | Optional | Gmail address if using SMTP fallback. |
| `EMAIL_PASSWORD` | Optional | 16-character Google App Password (if using Gmail SMTP). |

### 3. Configure Repository Variables (Optional)
Navigate to: **Settings → Secrets and variables → Actions → Variables → New repository variable**

| Variable Name | Default | Options / Example |
| :--- | :--- | :--- |
| `TIMEZONE` | `Asia/Kolkata` | Any IANA timezone (e.g. `UTC`, `America/New_York`). |
| `EMAIL_PROVIDER` | `resend` | `resend` or `smtp`. |
| `EMAIL_FROM` | `Personal AI Digest <onboarding@resend.dev>` | Verified sender address or domain in Resend. |
| `LLM_PROVIDER` | `claude` | `claude` or `openai`. |
| `LLM_MODEL` | `claude-3-5-sonnet-20241022` | Claude or OpenAI model identifier. |

### 4. Enable Workflow Permissions
Go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions** (needed for committing the markdown digest history back to `summaries/`).

---

## 💻 Local Development & CLI Usage

### Installation
```bash
# Clone repository
git clone https://github.com/guo-yichen/news-summary.git
cd news-summary

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup
Copy the template and fill in your keys:
```bash
cp .env.example .env
```

### Running via CLI
```bash
# Test execution (offline dry-run with preview HTML output)
python -m src.cli --type test --dry-run --mock-llm

# Run morning digest
python -m src.cli --type morning

# Run evening digest
python -m src.cli --type evening

# Backward-compatible runner
python -m src.runner
```

When running in dry-run mode, the generated email is saved to:
`summaries/latest_preview.html`

---

## 🧪 Test Suite

Run the complete offline test suite with pytest:

```bash
pytest tests/ -v
```

Tests cover:
- ✅ **URL Canonicalization & Tracking Stripping** (`test_dedup.py`)
- ✅ **Title Similarity & Cross-Source Duplicate Clustering** (`test_dedup.py`)
- ✅ **Multi-factor Relevance Scoring & Agentic AI Weighting** (`test_scoring.py`)
- ✅ **Clickbait & Fluff Penalty Detection** (`test_scoring.py`)
- ✅ **State Management & 14-Day Expiration Cleanup** (`test_state.py`)
- ✅ **Config Loading & Environment Variable Overrides** (`test_config.py`)
- ✅ **Responsive HTML Email & Markdown Generation** (`test_formatter.py`)
- ✅ **End-to-End Pipeline Dry-Run** (`test_pipeline.py`)
- ✅ **CLI Schedule & Argument Detection** (`test_cli.py`)

---

## ❓ Troubleshooting & FAQ

### 1. I haven't received an email from Resend.
- If using Resend's free test tier (`onboarding@resend.dev`), Resend only permits sending to the email address registered with your Resend account.
- Verify that `EMAIL_TO` matches your Resend login email, or verify a custom domain in the Resend dashboard.

### 2. Can I use Gmail SMTP instead of Resend?
- Yes! In GitHub Secrets, set `EMAIL_USER` to your Gmail address and `EMAIL_PASSWORD` to a 16-character **Google App Password** (generated under Google Account → Security → 2-Step Verification → App passwords). Set variable `EMAIL_PROVIDER=smtp`.

### 3. What happens if an RSS feed is down?
- The collector encapsulates each source in exception handlers. If a feed times out or errors, it logs a warning and proceeds with all remaining sources.

### 4. How do I adjust the schedule?
- In [`.github/workflows/ai-digest.yml`](file:///.github/workflows/ai-digest.yml), update the cron expressions:
  - `30 0 * * *` = 00:30 UTC = 06:00 AM IST
  - `30 12 * * *` = 12:30 UTC = 06:00 PM IST

---

## 📄 License
MIT License. Crafted for aspiring and practicing AI Engineers and Agentic AI Developers.
