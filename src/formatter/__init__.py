"""Formatter module for email HTML and Markdown generation."""

from src.formatter.html_builder import build_html_email
from src.formatter.markdown_builder import build_markdown_digest

__all__ = ["build_html_email", "build_markdown_digest"]
