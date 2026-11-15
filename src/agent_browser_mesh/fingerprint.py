"""Backwards-compatible shim for agent_browser_mesh.core.fingerprint."""

from .core.fingerprint import (
    AnchorRegistry,
    SemanticAnchor,
    create_semantic_anchor,
    generate_fingerprint_hash,
)

__all__ = [
    "SemanticAnchor",
    "AnchorRegistry",
    "create_semantic_anchor",
    "generate_fingerprint_hash",
]
