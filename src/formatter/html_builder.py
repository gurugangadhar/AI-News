"""Responsive, modern HTML email generator for AI Engineer Daily Digest."""

import html
from typing import List, Optional
from src.models import DigestContent, ProjectIdea, StorySummary


def _esc(text: Optional[str]) -> str:
    """Escape text for safe HTML embedding."""
    if not text:
        return ""
    return html.escape(str(text))


def _render_story_card(story: StorySummary, is_top: bool = False) -> str:
    """Render a single story card with senior AI engineer briefing layout."""
    border_color = "#3b82f6" if is_top else "#e2e8f0"
    badge_bg = "#eff6ff" if is_top else "#f1f5f9"
    badge_color = "#1d4ed8" if is_top else "#475569"
    badge_label = "🔥 TOP STORY" if is_top else story.category.replace("_", " ").upper()

    alt_links_html = ""
    if story.alternative_sources:
        alt_items = []
        for alt in story.alternative_sources:
            name = _esc(alt.get("name", "Alt Source"))
            url = alt.get("url", "#")
            alt_items.append(f'<a href="{url}" style="color:#64748b;text-decoration:underline;margin-right:8px;">{name}</a>')
        alt_links_html = f'<div style="font-size:12px;color:#94a3b8;margin-top:8px;">Also reported by: {" ".join(alt_items)}</div>'

    updated_badge = ""
    if story.is_updated:
        updated_badge = '<span style="background-color:#fef3c7;color:#b45309;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:700;margin-left:6px;">UPDATED</span>'

    card_html = f"""
    <div style="background-color:#ffffff;border:1px solid {border_color};border-radius:8px;padding:16px 18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
      <div style="margin-bottom:8px;">
        <span style="background-color:{badge_bg};color:{badge_color};padding:3px 8px;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:0.5px;">{badge_label}</span>
        {updated_badge}
        <span style="font-size:12px;color:#64748b;margin-left:8px;">via <strong>{_esc(story.source_name)}</strong></span>
      </div>
      <h3 style="margin:6px 0 10px 0;font-size:16px;line-height:1.4;color:#0f172a;">
        <a href="{story.primary_url}" style="color:#0f172a;text-decoration:none;" target="_blank">{_esc(story.title)}</a>
      </h3>

      <div style="font-size:13px;line-height:1.5;color:#334155;margin-bottom:8px;">
        <strong style="color:#0f172a;">What happened:</strong> {_esc(story.what_happened)}
      </div>

      <div style="font-size:13px;line-height:1.5;color:#334155;margin-bottom:8px;background-color:#f8fafc;padding:8px 10px;border-left:3px solid #3b82f6;border-radius:0 4px 4px 0;">
        <strong style="color:#1e3a8a;">Why it matters:</strong> {_esc(story.why_it_matters)}
      </div>

      <div style="font-size:13px;line-height:1.5;color:#334155;margin-bottom:8px;">
        <strong style="color:#047857;">Developer impact:</strong> {_esc(story.developer_impact)}
      </div>

      <div style="font-size:13px;line-height:1.5;color:#475569;margin-bottom:10px;">
        <strong style="color:#7c3aed;">Takeaway:</strong> {_esc(story.practical_takeaway)}
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid #f1f5f9;padding-top:8px;">
        <a href="{story.primary_url}" style="font-size:12px;font-weight:600;color:#2563eb;text-decoration:none;" target="_blank">Read Original Source &rarr;</a>
        {alt_links_html}
      </div>
    </div>
    """
    return card_html


def _render_section(title: str, icon: str, stories: List[StorySummary], is_top: bool = False) -> str:
    """Render a section with header and story cards."""
    if not stories:
        return ""

    cards = [_render_story_card(s, is_top=is_top) for s in stories]
    return f"""
    <div style="margin-top:24px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;margin-bottom:12px;border-bottom:2px solid #e2e8f0;padding-bottom:6px;">
        <h2 style="margin:0;font-size:17px;font-weight:700;color:#0f172a;letter-spacing:-0.2px;">
          <span style="margin-right:6px;">{icon}</span> {title}
        </h2>
        <span style="margin-left:auto;font-size:12px;color:#94a3b8;font-weight:600;">{len(stories)} stories</span>
      </div>
      {''.join(cards)}
    </div>
    """


def _render_what_to_learn(items: List[str]) -> str:
    """Render practical learning steps."""
    if not items:
        return ""
    lis = "".join([f'<li style="margin-bottom:8px;line-height:1.5;color:#1e293b;">{_esc(it)}</li>' for it in items])
    return f"""
    <div style="background-color:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px 18px;margin-top:24px;margin-bottom:16px;">
      <h2 style="margin:0 0 10px 0;font-size:16px;color:#166534;font-weight:700;">
        <span style="margin-right:6px;">📚</span> WHAT TO LEARN TODAY
      </h2>
      <ol style="margin:0;padding-left:20px;font-size:13px;">
        {lis}
      </ol>
    </div>
    """


def _render_project_idea(project: Optional[ProjectIdea]) -> str:
    """Render portfolio project idea."""
    if not project or not project.title:
        return ""

    tech_badges = "".join([
        f'<span style="background-color:#e0e7ff;color:#3730a3;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600;margin-right:6px;">{_esc(t)}</span>'
        for t in project.technologies
    ])

    return f"""
    <div style="background-color:#faf5ff;border:1px solid #e9d5ff;border-radius:8px;padding:16px 18px;margin-top:20px;margin-bottom:16px;">
      <div style="margin-bottom:6px;">
        <span style="background-color:#9333ea;color:#ffffff;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:700;">PROJECT IDEA</span>
        <span style="font-size:11px;color:#6b21a8;margin-left:8px;font-weight:600;">Difficulty: {_esc(project.difficulty)}</span>
      </div>
      <h3 style="margin:4px 0 8px 0;font-size:15px;color:#581c87;font-weight:700;">{_esc(project.title)}</h3>
      <p style="margin:0 0 10px 0;font-size:13px;line-height:1.5;color:#3b0764;">{_esc(project.description)}</p>
      <div style="margin-bottom:8px;">{tech_badges}</div>
      <div style="font-size:12px;color:#6b21a8;font-style:italic;">
        <strong>Portfolio Value:</strong> {_esc(project.portfolio_value)}
      </div>
    </div>
    """


def _render_career_signals(signals: List[str]) -> str:
    """Render career signals."""
    if not signals:
        return ""
    lis = "".join([f'<li style="margin-bottom:6px;line-height:1.5;color:#1e293b;">{_esc(s)}</li>' for s in signals])
    return f"""
    <div style="background-color:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px 18px;margin-top:20px;margin-bottom:16px;">
      <h2 style="margin:0 0 8px 0;font-size:15px;color:#1e40af;font-weight:700;">
        <span style="margin-right:6px;">🎯</span> CAREER SIGNAL
      </h2>
      <ul style="margin:0;padding-left:18px;font-size:13px;">
        {lis}
      </ul>
    </div>
    """


def _render_quick_links(links: List[dict]) -> str:
    """Render secondary quick links."""
    if not links:
        return ""
    items = []
    for l in links[:8]:
        title = _esc(l.get("title", ""))
        url = l.get("url", "#")
        src = _esc(l.get("source", ""))
        items.append(f'<li style="margin-bottom:6px;font-size:12px;"><a href="{url}" style="color:#2563eb;text-decoration:none;" target="_blank">{title}</a> <span style="color:#94a3b8;">({src})</span></li>')

    return f"""
    <div style="border-top:1px dashed #cbd5e1;padding-top:16px;margin-top:24px;">
      <h3 style="margin:0 0 8px 0;font-size:14px;color:#475569;font-weight:700;">⚡ QUICK LINKS</h3>
      <ul style="margin:0;padding-left:18px;color:#64748b;">
        {''.join(items)}
      </ul>
    </div>
    """


def build_html_email(digest: DigestContent) -> str:
    """Assemble complete responsive HTML email."""
    period_title = f"{digest.period_label} &bull; {digest.date_display}"
    is_test_banner = ""
    if digest.digest_type == "test":
        is_test_banner = """
        <div style="background-color:#fef08a;color:#854d0e;padding:10px 14px;border-radius:6px;font-size:13px;font-weight:700;margin-bottom:16px;text-align:center;">
          🧪 TEST EXECUTION &bull; Digest verification mode with active source samples
        </div>
        """

    quiet_banner = ""
    if digest.is_quiet_window:
        quiet_banner = """
        <div style="background-color:#f1f5f9;border:1px solid #cbd5e1;padding:16px;border-radius:8px;margin-bottom:20px;text-align:center;">
          <h3 style="margin:0 0 6px 0;color:#475569;font-size:15px;">Quiet AI Update Window</h3>
          <p style="margin:0;font-size:13px;color:#64748b;">No high-priority architectural releases or breaking model announcements met the quality threshold during this 12-hour window.</p>
        </div>
        """

    # Render all story sections
    sections_html = [
        _render_section("TOP DEVELOPMENTS", "🔥", digest.top_stories, is_top=True),
        _render_section("AGENTIC AI", "🤖", digest.agentic_ai),
        _render_section("MODELS & GENERATIVE AI", "🧠", digest.models_llms),
        _render_section("AI ENGINEERING & RAG", "💻", digest.ai_engineering),
        _render_section("AI TOOLS & CODING", "🛠️", digest.ai_tools),
        _render_section("CLOUD AI (AZURE / GOOGLE / AWS)", "☁️", digest.cloud_ai),
        _render_section("GITHUB & OPEN SOURCE", "⭐", digest.github_oss),
        _render_section("PRACTICAL RESEARCH", "🔬", digest.research),
    ]

    content_body = "".join(s for s in sections_html if s)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Personal AI Engineer Daily Digest</title>
</head>
<body style="margin:0;padding:0;background-color:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;color:#1e293b;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f8fafc;padding:20px 10px;">
    <tr>
      <td align="center">
        <!-- Main Container -->
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:640px;background-color:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
          <!-- Header -->
          <tr>
            <td style="background-color:#0f172a;padding:24px 28px;text-align:left;">
              <div style="font-size:11px;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
                Personal AI Engineer Briefing
              </div>
              <h1 style="margin:0 0 6px 0;font-size:22px;color:#ffffff;font-weight:800;letter-spacing:-0.5px;">
                AI ENGINEER DAILY DIGEST
              </h1>
              <div style="font-size:13px;color:#94a3b8;font-weight:500;">
                {period_title} &bull; Timezone: {digest.timezone}
              </div>
            </td>
          </tr>

          <!-- Main Content Body -->
          <tr>
            <td style="padding:20px 24px;">
              {is_test_banner}
              {quiet_banner}
              {content_body}
              {_render_what_to_learn(digest.what_to_learn)}
              {_render_project_idea(digest.project_idea)}
              {_render_career_signals(digest.career_signals)}
              {_render_quick_links(digest.quick_links)}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#f1f5f9;border-top:1px solid #e2e8f0;padding:16px 24px;text-align:center;font-size:11px;color:#64748b;line-height:1.5;">
              Personal AI Engineer Daily Digest &bull; Automated twice-daily delivery (06:00 / 18:00 IST)<br>
              Curated for AI Engineering, Agentic AI, and Production LLM Systems.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
