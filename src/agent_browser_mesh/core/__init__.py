"""Core browser mesh engine, DOM-Delta compiler, semantic fingerprinting, actions, and guardrails."""

from .actions import ActionExecutor, ActionResult
from .dom_compiler import DOMCompiler, DOMDelta
from .engine import BrowserMesh, BrowserSessionState
from .fingerprint import AnchorRegistry, SemanticAnchor, create_semantic_anchor
from .guardrails import BrowserGuardrails, SecurityVerdict

__all__ = [
    "BrowserMesh",
    "BrowserSessionState",
    "BrowserGuardrails",
    "SecurityVerdict",
    "DOMCompiler",
    "DOMDelta",
    "SemanticAnchor",
    "AnchorRegistry",
    "create_semantic_anchor",
    "ActionExecutor",
    "ActionResult",
]
