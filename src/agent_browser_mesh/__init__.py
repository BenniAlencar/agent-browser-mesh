"""AgentBrowserMesh: High-speed, zero-token-waste autonomous browser engine for AI agents."""

__version__ = "1.0.0"

from agent_browser_mesh.core import BrowserMesh, BrowserSessionState
from agent_browser_mesh.guardrails import BrowserGuardrails, SecurityVerdict
from agent_browser_mesh.dom_compiler import DOMCompiler, DOMDelta
from agent_browser_mesh.fingerprint import SemanticAnchor, AnchorRegistry, create_semantic_anchor
from agent_browser_mesh.actions import ActionExecutor, ActionResult
from agent_browser_mesh.mcp_server import MCPServer

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
    "MCPServer",
]
