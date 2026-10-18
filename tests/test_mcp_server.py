import pytest
from agent_browser_mesh.mcp_server import MCPServer
from agent_browser_mesh.core import BrowserMesh


def test_mcp_server_tool_definitions():
    server = MCPServer()
    assert "browser_navigate" in server.tools
    assert "browser_snapshot" in server.tools
    assert "browser_click" in server.tools
    assert "browser_type" in server.tools
    assert "browser_extract" in server.tools
    assert "browser_security_status" in server.tools


def test_mcp_server_dispatch_flow():
    mesh = BrowserMesh()
    server = MCPServer(mesh=mesh)

    sample_html = "<html><head><title>MCP Test</title></head><body><button id='b1'>Start Agent</button></body></html>"
    # Navigate
    res_nav = server.dispatch("browser_navigate", {"url": "https://test.local", "html_override": sample_html})
    # Note: simulate with override via mesh directly
    mesh.navigate("https://test.local", html_override=sample_html)

    # Snapshot
    snapshot = server.dispatch("browser_snapshot", {})
    assert snapshot["title"] == "MCP Test"
    assert len(snapshot["anchors"]) == 1

    anchor_id = snapshot["anchors"][0]["anchor_id"]

    # Click
    click_res = server.dispatch("browser_click", {"target_anchor": anchor_id})
    assert click_res["success"]

    # Security status
    sec = server.dispatch("browser_security_status", {})
    assert sec["is_clean"]
