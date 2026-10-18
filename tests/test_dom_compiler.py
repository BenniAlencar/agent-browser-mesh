import pytest
from agent_browser_mesh.dom_compiler import DOMCompiler


def test_dom_compiler_noise_reduction_and_savings():
    compiler = DOMCompiler()
    sample_html = """
    <html>
        <head>
            <title>Test Portal</title>
            <script>var x = 100; function track() {}</script>
            <style>body { background: #000; font-size: 14px; }</style>
        </head>
        <body>
            <header>
                <nav>
                    <a href="/login" aria-label="Sign In">Sign In</a>
                    <a href="/pricing">Pricing</a>
                </nav>
            </header>
            <main>
                <h1>Welcome to Agent Portal</h1>
                <p>Build resilient AI agents that execute deterministically on the modern web.</p>
                <form action="/search">
                    <input type="text" placeholder="Search documentation..." name="q" />
                    <button type="submit" id="btn-search">Search Now</button>
                </form>
            </main>
        </body>
    </html>
    """
    delta = compiler.compile(sample_html, url="https://example.com")
    
    assert delta.title == "Test Portal"
    assert delta.token_savings_pct > 30.0
    assert len(delta.anchors) >= 4
    assert "Sign In" in delta.markdown_view
    assert "Pricing" in delta.markdown_view
    assert "Search documentation..." in delta.markdown_view
    assert "Search Now" in delta.markdown_view
    # Ensure script and style noise were completely removed
    assert "var x = 100" not in delta.markdown_view
    assert "background: #000" not in delta.markdown_view


def test_empty_dom_handling():
    compiler = DOMCompiler()
    delta = compiler.compile("", url="about:blank")
    assert delta.markdown_view == "[EMPTY_PAGE]"
    assert delta.estimated_tokens == 0
    assert len(delta.anchors) == 0
