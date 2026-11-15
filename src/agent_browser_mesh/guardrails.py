"""Backwards-compatible shim for agent_browser_mesh.core.guardrails."""

from .core.guardrails import BrowserGuardrails, SecurityVerdict

__all__ = ["BrowserGuardrails", "SecurityVerdict"]
