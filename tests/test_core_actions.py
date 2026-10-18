import pytest
from agent_browser_mesh.core import BrowserMesh


def test_core_navigation_and_dom_action_flow():
    mesh = BrowserMesh()
    sample_html = """
    <html>
        <head><title>Sovereign Workspace</title></head>
        <body>
            <h1>Dashboard</h1>
            <input type="text" placeholder="Project Name" id="proj-name" />
            <button type="submit" id="create-btn">Create Repository</button>
        </body>
    </html>
    """
    nav_res = mesh.navigate("https://app.benni.ai/workspace", html_override=sample_html)
    assert nav_res.success
    assert "Sovereign Workspace" in nav_res.message
    
    delta = mesh.snapshot()
    assert delta.title == "Sovereign Workspace"
    assert len(delta.anchors) == 2

    # Find the input and button anchors
    inp_anchor = next(a for a in delta.anchors if a.tag == "input")
    btn_anchor = next(a for a in delta.anchors if a.tag == "button")

    # Type action
    type_res = mesh.type_text(inp_anchor.anchor_id, "agent-browser-mesh")
    assert type_res.success
    assert "agent-browser-mesh" in type_res.message

    # Click action
    click_res = mesh.click(btn_anchor.anchor_id)
    assert click_res.success
    assert "Create Repository" in click_res.message

    # Scroll action
    scroll_res = mesh.scroll("down", 300)
    assert scroll_res.success

    # Extract action
    data = mesh.extract()
    assert data["title"] == "Sovereign Workspace"
    assert len(data["anchors"]) == 2


def test_core_security_interception_on_navigation():
    mesh = BrowserMesh()
    # Attempt SSRF attack to cloud metadata
    nav_res = mesh.navigate("http://169.254.169.254/computeMetadata/v1/")
    assert not nav_res.success
    assert "SECURITY_BLOCKED" in nav_res.message

    status = mesh.get_security_status()
    assert not status["is_clean"]
    assert "SSRF_METADATA_ATTEMPT" in status["violations_recorded"]
