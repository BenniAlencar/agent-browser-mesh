"""Resilient Semantic Multi-Attribute Fingerprinting for Web Elements.

Eliminates brittle numeric indices and ephemeral CSS selectors.
Elements are anchored by invariant tuples:
(role, aria_label, normalized_text, tag_name, spatial_quadrant).
"""

from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SemanticAnchor(BaseModel):
    """An immutable, content-addressed anchor for an actionable web element."""
    anchor_id: str = Field(..., description="Short deterministic handle, e.g. 'btn-submit-a4f2'")
    tag: str = Field(..., description="HTML tag name: button, a, input, etc.")
    role: str = Field(default="generic", description="ARIA or semantic role: button, link, searchbox")
    aria_label: Optional[str] = Field(default=None, description="Accessible label")
    text: str = Field(default="", description="Visible trimmed inner text")
    input_type: Optional[str] = Field(default=None, description="Type attribute for inputs")
    is_interactive: bool = Field(default=True, description="Whether element accepts input/clicks")
    href: Optional[str] = Field(default=None, description="Target destination if link")
    quadrant: str = Field(default="center", description="Spatial quadrant: top-left, top-right, bottom, center")
    css_selector: str = Field(default="", description="Best-effort fallback CSS selector")
    fingerprint_hash: str = Field(..., description="SHA-256 derived content hash")


def normalize_text(text: Optional[str]) -> str:
    """Normalizes whitespace and removes noise characters."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text[:120]  # Cap at reasonable length for semantic identity


def generate_fingerprint_hash(
    tag: str,
    role: str,
    aria_label: Optional[str],
    text: str,
    input_type: Optional[str] = None
) -> str:
    """Computes a collision-resistant stable hash for an element."""
    payload = f"{tag.lower()}:{role.lower()}:{normalize_text(aria_label).lower()}:{normalize_text(text).lower()}:{(input_type or '').lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]


def create_semantic_anchor(
    tag: str,
    role: Optional[str] = None,
    aria_label: Optional[str] = None,
    text: str = "",
    input_type: Optional[str] = None,
    href: Optional[str] = None,
    quadrant: str = "center",
    css_selector: str = ""
) -> SemanticAnchor:
    """Creates a calibrated SemanticAnchor with short human-readable handle."""
    clean_tag = tag.lower().strip()
    clean_text = normalize_text(text)
    clean_role = (role or clean_tag).lower().strip()
    
    hash_key = generate_fingerprint_hash(clean_tag, clean_role, aria_label, clean_text, input_type)
    
    # Generate human-readable prefix: e.g. "btn-login-8a2f" or "input-email-1c4b"
    label_slug = re.sub(r"[^a-zA-Z0-9]+", "-", (aria_label or clean_text or clean_tag).strip().lower()).strip("-")
    label_slug = label_slug[:16] if label_slug else clean_tag
    anchor_id = f"@{clean_tag[:4]}-{label_slug}-{hash_key[:4]}"

    return SemanticAnchor(
        anchor_id=anchor_id,
        tag=clean_tag,
        role=clean_role,
        aria_label=aria_label,
        text=clean_text,
        input_type=input_type,
        href=href,
        quadrant=quadrant,
        css_selector=css_selector,
        fingerprint_hash=hash_key
    )


class AnchorRegistry:
    """Registry maintaining current active anchors and fuzzy fallback resolution."""

    def __init__(self):
        self._anchors: Dict[str, SemanticAnchor] = {}
        self._by_hash: Dict[str, SemanticAnchor] = {}

    def register(self, anchor: SemanticAnchor):
        self._anchors[anchor.anchor_id] = anchor
        self._by_hash[anchor.fingerprint_hash] = anchor

    def get_by_id(self, anchor_id: str) -> Optional[SemanticAnchor]:
        return self._anchors.get(anchor_id)

    def resolve(self, query: str) -> Optional[SemanticAnchor]:
        """Resolves target anchor by exact ID, hash, or semantic fuzzy match."""
        query_clean = query.strip()
        
        # 1. Exact ID match
        if query_clean in self._anchors:
            return self._anchors[query_clean]

        # 2. Hash match
        if query_clean in self._by_hash:
            return self._by_hash[query_clean]

        # 3. Fuzzy search by text or aria_label
        query_lower = query_clean.lower()
        candidates: List[tuple[int, SemanticAnchor]] = []

        for anchor in self._anchors.values():
            score = 0
            if query_lower in anchor.text.lower():
                score += 50
            if anchor.aria_label and query_lower in anchor.aria_label.lower():
                score += 60
            if query_lower in anchor.anchor_id.lower():
                score += 40
            if score > 0:
                candidates.append((score, anchor))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]

        return None

    def list_all(self) -> List[SemanticAnchor]:
        return list(self._anchors.values())

    def clear(self):
        self._anchors.clear()
        self._by_hash.clear()
