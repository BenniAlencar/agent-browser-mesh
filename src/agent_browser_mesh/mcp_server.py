"""Native Model Context Protocol (MCP) Server for BrowserMesh.

Exposes standard JSON-RPC tools for Claude Desktop, Cursor, Codex, and LLM Agents:
- browser_navigate: Navigates to a URL with SSRF protection.
- browser_snapshot: Returns ultra-compact DOM-Delta (<150 tokens).
- browser_click: Clicks on a resilient semantic anchor.
- browser_type: Types text into a form or search input.
- browser_extract: Extracts clean structured page content.
- browser_security_status: Returns audit violations and protection status.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

from agent_browser_mesh.core import BrowserMesh


class MCPServer:
    """Standard JSON-RPC 2.0 Model Context Protocol Server."""

    def __init__(self, mesh: BrowserMesh | None = None):
        self.mesh = mesh or BrowserMesh(strict_security=True)
        self.tools = {
            "browser_navigate": {
                "description": "Navigate to a URL with Tier-0 SSRF protection and DOM compaction.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target webpage URL (HTTP/HTTPS)"}
                    },
                    "required": ["url"]
                }
            },
            "browser_snapshot": {
                "description": "Get an ultra-compact DOM-Delta view of the current page (saves 92% tokens).",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "browser_click": {
                "description": "Click an interactive element by its semantic anchor ID (e.g. '@butt-submit-a4f2').",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_anchor": {"type": "string", "description": "Anchor ID or semantic fuzzy label"}
                    },
                    "required": ["target_anchor"]
                }
            },
            "browser_type": {
                "description": "Type text into an input field designated by its anchor ID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_anchor": {"type": "string", "description": "Input anchor ID or label"},
                        "text": {"type": "string", "description": "Text string to enter"}
                    },
                    "required": ["target_anchor", "text"]
                }
            },
            "browser_extract": {
                "description": "Extract structured text and actionable elements without vision token overhead.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Optional search filter query"}
                    }
                }
            },
            "browser_security_status": {
                "description": "Get current security audit status and blocked SSRF/injection events.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }

    def dispatch(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches an MCP tool call."""
        if tool_name == "browser_navigate":
            res = self.mesh.navigate(arguments.get("url", ""))
            return res.model_dump()
        elif tool_name == "browser_snapshot":
            delta = self.mesh.snapshot()
            return delta.model_dump()
        elif tool_name == "browser_click":
            res = self.mesh.click(arguments.get("target_anchor", ""))
            return res.model_dump()
        elif tool_name == "browser_type":
            res = self.mesh.type_text(arguments.get("target_anchor", ""), arguments.get("text", ""))
            return res.model_dump()
        elif tool_name == "browser_extract":
            return self.mesh.extract(arguments.get("query", ""))
        elif tool_name == "browser_security_status":
            return self.mesh.get_security_status()
        else:
            raise ValueError(f"Unknown tool: '{tool_name}'")

    def run_stdio(self):
        """Runs the standard MCP stdio loop."""
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                req_id = request.get("id")
                method = request.get("method")

                if method == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "tools": [
                                {"name": k, **v} for k, v in self.tools.items()
                            ]
                        }
                    }
                elif method == "tools/call":
                    params = request.get("params", {})
                    name = params.get("name")
                    args = params.get("arguments", {})
                    result = self.dispatch(name, args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {"type": "text", "text": json.dumps(result, indent=2)}
                            ]
                        }
                    }
                elif method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "agent-browser-mesh", "version": "1.0.0"}
                        }
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {}
                    }
                print(json.dumps(response), flush=True)
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(err_resp), flush=True)
