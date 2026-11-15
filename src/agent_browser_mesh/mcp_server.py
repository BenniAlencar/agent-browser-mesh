"""Backwards-compatible shim for agent_browser_mesh.serve.mcp_bridge."""

from .serve.mcp_bridge import MCPServer

__all__ = ["MCPServer"]
