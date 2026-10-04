"""Markdown generator for archiving daily digests in repository."""

from src.models import DigestContent, StorySummary


def _render_md_story(story: StorySummary, is_top: bool = False) -> str:
    lines = []
    prefix = "🔥 " if is_top else ""
    lines.append(f"### {prefix}[{story.title}]({story.primary_url})")
    lines.append(f"*Source: {story.source_name}*")
    if story.is_updated:
        lines.append("**[UPDATED]**")
    lines.append("")
    lines.append(f"- **What happened**: {story.what_happened}")
    lines.append(f"- **Why it matters**: {story.why_it_matters}")
    lines.append(f"- **Developer impact**: {story.developer_impact}")
    lines.append(f"- **Practical takeaway**: {story.practical_takeaway}")

    if story.alternative_sources:
        alts = [f"[{a.get('name', 'Alt')}]({a.get('url', '#')})" for a in story.alternative_sources]
        lines.append(f"- *Also covered by: {', '.join(alts)}*")

    lines.append("")
    return "\n".join(lines)


def build_markdown_digest(digest: DigestContent) -> str:
    """Build markdown representation of the digest."""
    doc = []
    doc.append(f"# AI Engineer Daily Digest — {digest.period_label}")
    doc.append(f"**Date**: {digest.date_display} ({digest.timezone})\n")

    if digest.digest_type == "test":
        doc.append("> 🧪 **Note**: This was generated in test verification mode.\n")

    if digest.is_quiet_window:
        doc.append("> ℹ️ **Quiet AI Update Window**: No critical announcements exceeded threshold.\n")

    def add_section(title: str, stories: list):
        if stories:
            doc.append(f"## {title}\n")
            for s in stories:
                doc.append(_render_md_story(s, is_top=("TOP" in title)))

    add_section("🔥 Top 5 Developments", digest.top_stories)
    add_section("🤖 Agentic AI", digest.agentic_ai)
    add_section("🧠 Models & LLMs", digest.models_llms)
    add_section("💻 AI Engineering & RAG", digest.ai_engineering)
    add_section("🛠️ AI Tools & Coding", digest.ai_tools)
    add_section("☁️ Cloud AI (Azure / Google / AWS)", digest.cloud_ai)
    add_section("⭐ GitHub & Open Source", digest.github_oss)
    add_section("🔬 Research", digest.research)

    if digest.what_to_learn:
        doc.append("## 📚 What to Learn Today\n")
        for idx, item in enumerate(digest.what_to_learn, 1):
            doc.append(f"{idx}. {item}")
        doc.append("")

    if digest.project_idea:
        pi = digest.project_idea
        doc.append("## 🚀 Project Idea\n")
        doc.append(f"### {pi.title}")
        doc.append(f"{pi.description}\n")
        doc.append(f"- **Difficulty**: {pi.difficulty}")
        doc.append(f"- **Technologies**: {', '.join(pi.technologies)}")
        doc.append(f"- **Portfolio Value**: {pi.portfolio_value}\n")

    if digest.career_signals:
        doc.append("## 🎯 Career Signals\n")
        for sig in digest.career_signals:
            doc.append(f"- {sig}")
        doc.append("")

    if digest.quick_links:
        doc.append("## ⚡ Quick Links\n")
        for q in digest.quick_links:
            doc.append(f"- [{q.get('title')}]({q.get('url')}) ({q.get('source')})")
        doc.append("")

    return "\n".join(doc)
