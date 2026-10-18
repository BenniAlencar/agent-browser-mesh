"""Command-line interface for agent-browser-mesh."""

from __future__ import annotations

import sys
import click
from agent_browser_mesh.core import BrowserMesh
from agent_browser_mesh.mcp_server import MCPServer


@click.group()
@click.version_option(version="1.0.0", prog_name="agent-browser-mesh")
def main():
    """AgentBrowserMesh: Sovereign, High-Speed AI Browser Automation Engine."""
    pass


@main.command()
@click.argument("url")
@click.option("--no-strict", is_flag=True, help="Disable strict security guardrails")
def inspect(url: str, no_strict: bool):
    """Navigate to URL, compact DOM, and display token savings analysis."""
    click.echo(f"[*] Initializing BrowserMesh on {url}...")
    mesh = BrowserMesh(strict_security=not no_strict)
    result = mesh.navigate(url)

    if not result.success:
        click.secho(f"[!] Navigation Failed: {result.message}", fg="red")
        sys.exit(1)

    delta = mesh.snapshot()
    click.secho(f"[✓] Title: {delta.title}", fg="green", bold=True)
    click.echo(f"[-] Raw Size: {delta.raw_size_bytes} bytes | Compact Size: {delta.compact_size_bytes} bytes")
    click.secho(f"[⚡] Token Savings: {delta.token_savings_pct}% (~{delta.estimated_tokens} tokens vs ~{delta.raw_size_bytes//4} raw)", fg="cyan")
    click.echo(f"[-] Actionable Anchors Found: {len(delta.anchors)}\n")

    click.echo("--- Compact DOM-Delta Preview ---")
    click.echo(delta.markdown_view[:1200] + ("\n... [truncated]" if len(delta.markdown_view) > 1200 else ""))


@main.command()
def mcp():
    """Launch the stdio Model Context Protocol (MCP) server for Claude / Cursor / Codex."""
    server = MCPServer()
    server.run_stdio()


@main.command()
def benchmark():
    """Run an empirical token compression and latency benchmark."""
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>E-Commerce Storefront</title><script>console.log('noise');</script><style>.box{color:red;}</style></head>
    <body>
        <header><nav><a href="/home">Home</a><a href="/deals">Deals</a><a href="/cart">Cart (3)</a></nav></header>
        <main>
            <h1>Wireless Noise-Canceling Headphones</h1>
            <p>Experience studio-grade acoustics with 40-hour battery life and adaptive ANC.</p>
            <div class="reviews"><span>★★★★★ 4.9 (1,248 reviews)</span></div>
            <div class="pricing"><span class="price">$199.99</span></div>
            <form action="/checkout" method="POST">
                <label for="qty">Quantity</label>
                <input type="number" id="qty" name="quantity" value="1" min="1" max="5" />
                <button type="submit" id="buy-btn" aria-label="Add to Shopping Cart">Add to Cart</button>
            </form>
        </main>
        <footer><p>© 2026 Store Inc. All rights reserved.</p></footer>
    </body>
    </html>
    """
    click.secho("=== AgentBrowserMesh Token Compression Benchmark ===", fg="yellow", bold=True)
    mesh = BrowserMesh()
    mesh.navigate("https://example.com/store", html_override=sample_html)
    delta = mesh.snapshot()

    click.echo(f"Raw HTML bytes:      {delta.raw_size_bytes} bytes (~{delta.raw_size_bytes // 4} tokens)")
    click.echo(f"Compact Delta bytes: {delta.compact_size_bytes} bytes (~{delta.estimated_tokens} tokens)")
    click.secho(f"Token Reduction:     {delta.token_savings_pct}%", fg="green", bold=True)
    click.echo(f"Anchors Identified:  {len(delta.anchors)}")
    for a in delta.anchors:
        click.echo(f"  * {a.anchor_id} -> <{a.tag}> role={a.role} text='{a.text or a.aria_label}'")



if __name__ == "__main__":
    main()
