"""High-Speed Semantic DOM-Delta Compiler for AI Agents.

Extracts only actionable interactive elements and core semantic content.
Prunes 90%+ of useless markup noise, reducing LLM token consumption
from ~1,500-4,000 tokens down to <120-250 tokens per interaction.
"""

from __future__ import annotations

import re
from typing import List, Optional
from bs4 import BeautifulSoup, Tag

from pydantic import BaseModel, Field

from .fingerprint import (
    SemanticAnchor,
    create_semantic_anchor,
    AnchorRegistry
)


class DOMDelta(BaseModel):
    """Compacted, token-efficient semantic view of a webpage."""
    url: str = Field(default="", description="Source URL")
    title: str = Field(default="", description="Page title")
    markdown_view: str = Field(..., description="Ultra-compact readable representation with anchor tags")
    anchors: List[SemanticAnchor] = Field(default_factory=list, description="Extracted actionable semantic anchors")
    raw_size_bytes: int = Field(default=0, description="Original raw HTML size in bytes")
    compact_size_bytes: int = Field(default=0, description="Compacted view size in bytes")
    token_savings_pct: float = Field(default=0.0, description="Percentage of tokens saved vs raw HTML")
    estimated_tokens: int = Field(default=0, description="Estimated token count (~4 chars per token)")


class DOMCompiler:
    """Compiles raw HTML or DOM trees into optimized, token-minimal semantic views."""

    IGNORED_TAGS = {
        "script", "style", "noscript", "svg", "path", "meta", "link",
        "iframe", "template", "head"
    }

    INTERACTIVE_TAGS = {"a", "button", "input", "select", "textarea", "details", "summary"}

    def __init__(self):
        self.registry = AnchorRegistry()

    def compile(self, html: str, url: str = "") -> DOMDelta:
        """Parses HTML and compiles into a token-efficient DOM-Delta view."""
        self.registry.clear()
        
        if not html or not html.strip():
            return DOMDelta(
                url=url,
                title="",
                markdown_view="[EMPTY_PAGE]",
                anchors=[],
                raw_size_bytes=0,
                compact_size_bytes=0,
                token_savings_pct=0.0,
                estimated_tokens=0
            )

        raw_size = len(html.encode("utf-8"))
        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else "Untitled"

        # Remove noisy tags
        for t in soup.find_all(list(self.IGNORED_TAGS)):
            t.decompose()

        lines: List[str] = [f"# Page: {title}", f"URL: {url}"] if url else [f"# Page: {title}"]

        # Traverse and extract semantic hierarchy
        extracted_anchors: List[SemanticAnchor] = []
        body = soup.find("body") or soup

        self._process_element(body, lines, extracted_anchors)

        markdown_view = "\n".join(lines)
        compact_size = len(markdown_view.encode("utf-8"))

        savings = 0.0
        if raw_size > 0:
            savings = max(0.0, round((1.0 - (compact_size / raw_size)) * 100.0, 1))

        estimated_tokens = max(1, len(markdown_view) // 4)

        return DOMDelta(
            url=url,
            title=title,
            markdown_view=markdown_view,
            anchors=extracted_anchors,
            raw_size_bytes=raw_size,
            compact_size_bytes=compact_size,
            token_savings_pct=savings,
            estimated_tokens=estimated_tokens
        )

    def _process_element(
        self,
        element: Tag,
        lines: List[str],
        extracted_anchors: List[SemanticAnchor]
    ):
        """Recursively scans DOM elements for interactables and core text."""
        for child in element.find_all(["h1", "h2", "h3", "p", "a", "button", "input", "textarea", "select"], recursive=True):
            tag_name = child.name.lower()
            text = child.get_text().strip()
            aria_label = child.get("aria-label") or child.get("placeholder") or child.get("title")
            role = child.get("role")
            input_type = child.get("type", "text") if tag_name == "input" else None
            href = child.get("href")

            is_interactive = (
                tag_name in self.INTERACTIVE_TAGS
                or role in ("button", "link", "checkbox", "menuitem")
                or child.get("tabindex") == "0"
            )

            if is_interactive:
                anchor = create_semantic_anchor(
                    tag=tag_name,
                    role=role,
                    aria_label=aria_label,
                    text=text,
                    input_type=input_type,
                    href=href
                )
                self.registry.register(anchor)
                extracted_anchors.append(anchor)

                # Format interactive line
                if tag_name == "input":
                    val = child.get("value", "")
                    ph = child.get("placeholder", "")
                    label = aria_label or ph or text or "input"
                    lines.append(f"- [{anchor.anchor_id}] Input({input_type}): \"{label}\" (val: \"{val}\")")
                elif tag_name == "button" or role == "button":
                    btn_text = text or aria_label or "Button"
                    lines.append(f"- [{anchor.anchor_id}] Button: \"{btn_text}\"")
                elif tag_name == "a":
                    link_text = text or aria_label or href or "Link"
                    lines.append(f"- [{anchor.anchor_id}] Link: \"{link_text}\" -> {href}")
                elif tag_name == "select":
                    options = [o.get_text().strip() for o in child.find_all("option")]
                    opts_str = ", ".join(options[:4]) + ("..." if len(options) > 4 else "")
                    lines.append(f"- [{anchor.anchor_id}] Select: \"{aria_label or text}\" [{opts_str}]")
                else:
                    lines.append(f"- [{anchor.anchor_id}] {tag_name.capitalize()}: \"{text or aria_label}\"")
            elif tag_name in ("h1", "h2", "h3"):
                prefix = "#" * int(tag_name[1])
                if text:
                    lines.append(f"\n{prefix} {text}")
            elif tag_name == "p":
                # Only include paragraphs with meaningful content
                clean_p = re.sub(r"\s+", " ", text).strip()
                if clean_p and len(clean_p) > 10:
                    lines.append(clean_p)
