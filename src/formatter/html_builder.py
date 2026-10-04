"""Responsive, calm, and aesthetic HTML email generator for AI Engineer Daily Digest."""

import html
from typing import Dict, List, Optional
from src.models import DigestContent, ProjectIdea, StorySummary


def _esc(text: Optional[str]) -> str:
    """Escape text for safe HTML embedding."""
    if not text:
        return ""
    return html.escape(str(text))


# Soft, aesthetic category styles: (bg, text, border, label)
CATEGORY_THEMES: Dict[str, Dict[str, str]] = {
    "top_stories": {
        "bg": "#fef2f2",
        "text": "#991b1b",
        "border": "#fecaca",
        "label": "TOP STORY",
        "icon": "🔥",
    },
    "agentic_ai": {
        "bg": "#f5f3ff",
        "text": "#5b21b6",
        "border": "#ddd6fe",
        "label": "AGENTIC AI",
        "icon": "🤖",
    },
    "models_llms": {
        "bg": "#ecfeff",
        "text": "#155e75",
        "border": "#cffafe",
        "label": "FOUNDATION MODELS",
        "icon": "🧠",
    },
    "ai_engineering": {
        "bg": "#eff6ff",
        "text": "#1e40af",
        "border": "#dbeafe",
        "label": "AI ENGINEERING & RAG",
        "icon": "💻",
    },
    "ai_tools": {
        "bg": "#f0fdf4",
        "text": "#166534",
        "border": "#bbf7d0",
        "label": "AI TOOLS & CODING",
        "icon": "🛠️",
    },
    "cloud_ai": {
        "bg": "#f8fafc",
        "text": "#334155",
        "border": "#cbd5e1",
        "label": "CLOUD AI & ENTERPRISE",
        "icon": "☁️",
    },
    "github_oss": {
        "bg": "#fffbeb",
        "text": "#92400e",
        "border": "#fde68a",
        "label": "GITHUB & OPEN SOURCE",
        "icon": "⭐",
    },
    "research": {
        "bg": "#fdf4ff",
        "text": "#86198f",
        "border": "#f5d0fe",
        "label": "PRACTICAL RESEARCH",
        "icon": "🔬",
    },
}


def _get_category_theme(category: str, is_top: bool = False) -> Dict[str, str]:
    if is_top:
        return CATEGORY_THEMES["top_stories"]
    cat_key = category.lower().replace(" ", "_").replace("-", "_")
    return CATEGORY_THEMES.get(cat_key, {
        "bg": "#f1f5f9",
        "text": "#475569",
        "border": "#e2e8f0",
        "label": category.replace("_", " ").upper(),
        "icon": "📌",
    })


def _render_story_card(story: StorySummary, is_top: bool = False) -> str:
    """Render a calm, beautifully formatted story card with clear engineering hierarchy."""
    theme = _get_category_theme(story.category, is_top=is_top)

    alt_links_html = ""
    if story.alternative_sources:
        alt_items = []
        for alt in story.alternative_sources:
            name = _esc(alt.get("name", "Alt Source"))
            url = alt.get("url", "#")
            alt_items.append(
                f'<a href="{url}" style="color:#64748b;text-decoration:underline;text-underline-offset:2px;margin-right:8px;" target="_blank">{name}</a>'
            )
        alt_links_html = f"""
        <div style="font-size:11px;color:#94a3b8;margin-top:10px;padding-top:8px;border-top:1px dashed #f1f5f9;">
          <span style="font-weight:600;color:#64748b;">Alternative coverage:</span> {" &bull; ".join(alt_items)}
        </div>
        """

    updated_badge = ""
    if story.is_updated:
        updated_badge = '<span style="background-color:#fef3c7;color:#92400e;border:1px solid #fde68a;padding:2px 7px;border-radius:9999px;font-size:10px;font-weight:700;margin-left:6px;letter-spacing:0.5px;">UPDATED</span>'

    card_border = "#cbd5e1" if is_top else "#e2e8f0"

    return f"""
    <div style="background-color:#ffffff;border:1px solid {card_border};border-radius:10px;padding:18px 20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(15,23,42,0.03);">
      <!-- Card Header: Category & Source -->
      <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom:10px;">
        <tr>
          <td align="left">
            <span style="background-color:{theme['bg']};color:{theme['text']};border:1px solid {theme['border']};padding:3px 8px;border-radius:6px;font-size:10.5px;font-weight:700;letter-spacing:0.4px;">
              {theme['icon']} {theme['label']}
            </span>
            {updated_badge}
          </td>
          <td align="right" style="font-size:11.5px;color:#64748b;">
            via <strong style="color:#334155;">{_esc(story.source_name)}</strong>
          </td>
        </tr>
      </table>

      <!-- Headline -->
      <h3 style="margin:0 0 10px 0;font-size:16.5px;font-weight:700;line-height:1.4;color:#0f172a;">
        <a href="{story.primary_url}" style="color:#0f172a;text-decoration:none;" target="_blank">
          {_esc(story.title)}
        </a>
      </h3>

      <!-- What Happened -->
      <div style="font-size:13.5px;line-height:1.6;color:#334155;margin-bottom:10px;">
        <span style="font-weight:600;color:#0f172a;">What happened:</span> {_esc(story.what_happened)}
      </div>

      <!-- Why It Matters (Serene Tinted Callout) -->
      <div style="background-color:#f8fafc;border-left:3px solid #38bdf8;border-radius:0 6px 6px 0;padding:10px 14px;margin-bottom:10px;font-size:13px;line-height:1.55;color:#1e293b;">
        <div style="font-weight:700;color:#0369a1;font-size:11.5px;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:2px;">
          💡 Why It Matters
        </div>
        {_esc(story.why_it_matters)}
      </div>

      <!-- Developer Impact -->
      <div style="font-size:13px;line-height:1.55;color:#334155;margin-bottom:10px;">
        <span style="font-weight:600;color:#0f766e;">🛠️ Developer Impact:</span> {_esc(story.developer_impact)}
      </div>

      <!-- Practical Takeaway -->
      <div style="background-color:#fcfcfd;border:1px solid #f1f5f9;border-radius:6px;padding:8px 12px;margin-bottom:12px;font-size:12.5px;line-height:1.5;color:#475569;">
        <span style="font-weight:700;color:#6b21a8;">⚡ Takeaway:</span> {_esc(story.practical_takeaway)}
      </div>

      <!-- Action Row -->
      <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-top:1px solid #f1f5f9;padding-top:10px;margin-top:4px;">
        <tr>
          <td align="left">
            <a href="{story.primary_url}" style="display:inline-block;background-color:#f1f5f9;color:#0f172a;padding:5px 11px;border-radius:6px;font-size:11.5px;font-weight:600;text-decoration:none;" target="_blank">
              Read Original Source &rarr;
            </a>
          </td>
          <td align="right" style="font-size:11.5px;color:#94a3b8;">
            <a href="{story.primary_url}" style="color:#64748b;text-decoration:none;" target="_blank">Full Post &bull; Link</a>
          </td>
        </tr>
      </table>

      {alt_links_html}
    </div>
    """


def _render_section(title: str, icon: str, section_id: str, stories: List[StorySummary], is_top: bool = False) -> str:
    """Render a clean semantic section with an anchor id for quick-jump navigation."""
    if not stories:
        return ""

    cards = [_render_story_card(s, is_top=is_top) for s in stories]
    return f"""
    <div id="{section_id}" style="margin-top:28px;margin-bottom:16px;">
      <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom:12px;border-bottom:1.5px solid #e2e8f0;padding-bottom:8px;">
        <tr>
          <td align="left">
            <h2 style="margin:0;font-size:16px;font-weight:800;color:#0f172a;letter-spacing:-0.2px;">
              <span style="margin-right:6px;">{icon}</span> {title}
            </h2>
          </td>
          <td align="right">
            <span style="font-size:11px;font-weight:600;color:#64748b;background-color:#f1f5f9;padding:2px 8px;border-radius:9999px;">
              {len(stories)} stories
            </span>
          </td>
        </tr>
      </table>
      {''.join(cards)}
    </div>
    """


def _render_what_to_learn(items: List[str]) -> str:
    """Render practical learning steps in a serene sage card."""
    if not items:
        return ""
    lis = "".join([
        f'<li style="margin-bottom:10px;line-height:1.55;color:#1e293b;padding-left:4px;">{_esc(it)}</li>'
        for it in items
    ])
    return f"""
    <div id="section-learn" style="background-color:#f0fdf4;border:1px solid #dcfce7;border-radius:10px;padding:20px;margin-top:28px;margin-bottom:18px;">
      <div style="font-size:11px;font-weight:700;color:#166534;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">
        Continuous Upskilling
      </div>
      <h2 style="margin:0 0 12px 0;font-size:16px;color:#14532d;font-weight:800;">
        <span style="margin-right:6px;">📚</span> WHAT TO LEARN TODAY
      </h2>
      <ol style="margin:0;padding-left:22px;font-size:13.5px;">
        {lis}
      </ol>
    </div>
    """


def _render_project_idea(project: Optional[ProjectIdea]) -> str:
    """Render portfolio project idea as a clean engineering blueprint."""
    if not project or not project.title:
        return ""

    tech_badges = "".join([
        f'<span style="background-color:#f5f3ff;color:#5b21b6;border:1px solid #ddd6fe;padding:2px 7px;border-radius:4px;font-size:11px;font-weight:600;margin-right:6px;display:inline-block;margin-bottom:4px;">{_esc(t)}</span>'
        for t in project.technologies
    ])

    return f"""
    <div id="section-project" style="background-color:#faf5ff;border:1px solid #e9d5ff;border-radius:10px;padding:20px;margin-top:24px;margin-bottom:18px;">
      <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom:8px;">
        <tr>
          <td align="left">
            <span style="background-color:#7e22ce;color:#ffffff;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700;letter-spacing:0.5px;">PROJECT BLUEPRINT</span>
            <span style="font-size:11px;color:#6b21a8;margin-left:8px;font-weight:600;">Difficulty: {_esc(project.difficulty)}</span>
          </td>
        </tr>
      </table>
      <h3 style="margin:4px 0 8px 0;font-size:15.5px;color:#4c1d95;font-weight:700;">{_esc(project.title)}</h3>
      <p style="margin:0 0 12px 0;font-size:13.5px;line-height:1.6;color:#3b0764;">{_esc(project.description)}</p>
      <div style="margin-bottom:10px;">{tech_badges}</div>
      <div style="background-color:#f3e8ff;border-radius:6px;padding:8px 12px;font-size:12px;color:#581c87;line-height:1.5;">
        <strong>Portfolio Value:</strong> {_esc(project.portfolio_value)}
      </div>
    </div>
    """


def _render_career_signals(signals: List[str]) -> str:
    """Render career signals as serene telemetry bullets."""
    if not signals:
        return ""
    lis = "".join([
        f'<li style="margin-bottom:8px;line-height:1.5;color:#1e293b;padding-left:4px;">{_esc(s)}</li>'
        for s in signals
    ])
    return f"""
    <div id="section-career" style="background-color:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:20px;margin-top:24px;margin-bottom:18px;">
      <div style="font-size:11px;font-weight:700;color:#0284c7;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:4px;">
        Market Intelligence
      </div>
      <h2 style="margin:0 0 10px 0;font-size:15px;color:#0369a1;font-weight:800;">
        <span style="margin-right:6px;">🎯</span> CAREER SIGNAL
      </h2>
      <ul style="margin:0;padding-left:20px;font-size:13px;">
        {lis}
      </ul>
    </div>
    """


def _render_quick_links(links: List[dict]) -> str:
    """Render secondary quick links in a clean two-column or clean list table."""
    if not links:
        return ""
    items = []
    for l in links[:8]:
        title = _esc(l.get("title", ""))
        url = l.get("url", "#")
        src = _esc(l.get("source", ""))
        items.append(
            f'<li style="margin-bottom:8px;font-size:12.5px;line-height:1.5;"><a href="{url}" style="color:#2563eb;text-decoration:none;font-weight:500;" target="_blank">{title}</a> <span style="color:#94a3b8;font-size:11px;">({src})</span></li>'
        )

    return f"""
    <div style="border-top:1px dashed #cbd5e1;padding-top:18px;margin-top:28px;">
      <h3 style="margin:0 0 10px 0;font-size:13.5px;color:#475569;font-weight:700;letter-spacing:0.3px;">⚡ QUICK LINKS & ARCHIVE</h3>
      <ul style="margin:0;padding-left:20px;color:#64748b;">
        {''.join(items)}
      </ul>
    </div>
    """


def build_html_email(digest: DigestContent) -> str:
    """Assemble complete aesthetic, calm, and highly functional responsive HTML email."""
    period_title = f"{digest.period_label} &bull; {digest.date_display}"

    is_test_banner = ""
    if digest.digest_type == "test":
        is_test_banner = """
        <div style="background-color:#fef9c3;color:#713f12;border:1px solid #fde047;padding:10px 14px;border-radius:8px;font-size:12.5px;font-weight:600;margin-bottom:18px;text-align:center;">
          🧪 TEST MODE &bull; Digest verification execution with active source feeds
        </div>
        """

    quiet_banner = ""
    if digest.is_quiet_window:
        quiet_banner = """
        <div style="background-color:#f8fafc;border:1px solid #e2e8f0;padding:18px;border-radius:10px;margin-bottom:20px;text-align:center;">
          <h3 style="margin:0 0 6px 0;color:#334155;font-size:15px;font-weight:700;">Quiet AI Update Window</h3>
          <p style="margin:0;font-size:13px;color:#64748b;line-height:1.5;">No breaking architectural releases or model announcements exceeded the quality threshold during this window.</p>
        </div>
        """

    # Quick Jump Navigation Bar
    nav_pills = []
    if digest.top_stories:
        nav_pills.append('<a href="#section-top" style="color:#475569;background-color:#f1f5f9;padding:4px 9px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;margin:3px 2px;display:inline-block;">🔥 Top</a>')
    if digest.agentic_ai:
        nav_pills.append('<a href="#section-agentic" style="color:#5b21b6;background-color:#f5f3ff;padding:4px 9px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;margin:3px 2px;display:inline-block;">🤖 Agents</a>')
    if digest.models_llms:
        nav_pills.append('<a href="#section-models" style="color:#155e75;background-color:#ecfeff;padding:4px 9px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;margin:3px 2px;display:inline-block;">🧠 Models</a>')
    if digest.ai_engineering:
        nav_pills.append('<a href="#section-engineering" style="color:#1e40af;background-color:#eff6ff;padding:4px 9px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;margin:3px 2px;display:inline-block;">💻 Engineering</a>')
    if digest.ai_tools:
        nav_pills.append('<a href="#section-tools" style="color:#166534;background-color:#f0fdf4;padding:4px 9px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;margin:3px 2px;display:inline-block;">🛠️ Tools</a>')
    if digest.cloud_ai:
        nav_pills.append('<a href="#section-cloud" style="color:#334155;background-color:#f8fafc;padding:4px 9px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;margin:3px 2px;display:inline-block;">☁️ Cloud</a>')
    if digest.what_to_learn:
        nav_pills.append('<a href="#section-learn" style="color:#14532d;background-color:#dcfce7;padding:4px 9px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;margin:3px 2px;display:inline-block;">📚 Learn</a>')

    nav_bar_html = ""
    if nav_pills:
        nav_bar_html = f"""
        <div style="background-color:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:8px 12px;margin-bottom:20px;text-align:center;">
          <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;margin-right:6px;letter-spacing:0.5px;">JUMP TO:</span>
          {' '.join(nav_pills)}
        </div>
        """

    # Render all story sections with semantic anchor IDs
    sections_html = [
        _render_section("TOP DEVELOPMENTS", "🔥", "section-top", digest.top_stories, is_top=True),
        _render_section("AGENTIC AI & ORCHESTRATION", "🤖", "section-agentic", digest.agentic_ai),
        _render_section("MODELS & GENERATIVE AI", "🧠", "section-models", digest.models_llms),
        _render_section("AI ENGINEERING & RAG", "💻", "section-engineering", digest.ai_engineering),
        _render_section("AI TOOLS & CODING AGENTS", "🛠️", "section-tools", digest.ai_tools),
        _render_section("CLOUD AI (AZURE / GOOGLE / AWS)", "☁️", "section-cloud", digest.cloud_ai),
        _render_section("GITHUB & OPEN SOURCE", "⭐", "section-github", digest.github_oss),
        _render_section("PRACTICAL RESEARCH", "🔬", "section-research", digest.research),
    ]

    content_body = "".join(s for s in sections_html if s)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Personal AI Engineer Daily Digest</title>
</head>
<body style="margin:0;padding:0;background-color:#f6f8fa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;color:#1e293b;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f6f8fa;padding:24px 10px;">
    <tr>
      <td align="center">
        <!-- Main Email Container -->
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:620px;background-color:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;box-shadow:0 4px 16px rgba(15,23,42,0.04);">
          
          <!-- Elegant Masthead Header -->
          <tr>
            <td style="background-color:#0b0f19;padding:28px 28px 24px 28px;text-align:left;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="left">
                    <span style="background-color:rgba(56,189,248,0.12);color:#38bdf8;border:1px solid rgba(56,189,248,0.25);padding:3px 8px;border-radius:9999px;font-size:10.5px;font-weight:700;letter-spacing:0.8px;text-transform:uppercase;">
                      Senior AI Briefing
                    </span>
                  </td>
                  <td align="right" style="font-size:11.5px;color:#94a3b8;">
                    ⏱️ ~4 min read
                  </td>
                </tr>
              </table>

              <h1 style="margin:12px 0 6px 0;font-size:22px;color:#ffffff;font-weight:800;letter-spacing:-0.4px;line-height:1.25;">
                AI ENGINEER DAILY DIGEST
              </h1>
              
              <div style="font-size:12.5px;color:#94a3b8;font-weight:400;margin-top:4px;">
                {period_title} &bull; Timezone: {digest.timezone}
              </div>
            </td>
          </tr>

          <!-- Main Content Body -->
          <tr>
            <td style="padding:22px 24px 28px 24px;">
              {is_test_banner}
              {quiet_banner}
              {nav_bar_html}
              {content_body}
              {_render_what_to_learn(digest.what_to_learn)}
              {_render_project_idea(digest.project_idea)}
              {_render_career_signals(digest.career_signals)}
              {_render_quick_links(digest.quick_links)}
            </td>
          </tr>

          <!-- Calm, Minimalist Footer -->
          <tr>
            <td style="background-color:#f8fafc;border-top:1px solid #e2e8f0;padding:20px 24px;text-align:center;font-size:11.5px;color:#64748b;line-height:1.6;">
              <div style="font-weight:600;color:#334155;margin-bottom:4px;">
                Personal AI Engineer Daily Digest
              </div>
              <div>Curated for AI Engineering, Agent Architectures & LLM Systems.</div>
              <div style="color:#94a3b8;margin-top:6px;font-size:10.5px;">
                Delivered twice daily at 06:00 AM & 06:00 PM IST &bull; Powered by Google Gemini & Resend
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
