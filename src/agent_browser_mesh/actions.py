"""Backwards-compatible shim for agent_browser_mesh.core.actions."""

from .core.actions import ActionExecutor, ActionResult

__all__ = ["ActionExecutor", "ActionResult"]
