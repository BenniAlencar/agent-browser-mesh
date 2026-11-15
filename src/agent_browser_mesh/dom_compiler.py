"""Backwards-compatible shim for agent_browser_mesh.core.dom_compiler."""

from .core.dom_compiler import DOMCompiler, DOMDelta

__all__ = ["DOMCompiler", "DOMDelta"]
