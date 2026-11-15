"""Minimal quickstart example for agent-browser-mesh (offline HTML override)."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agent_browser_mesh import BrowserMesh


def main() -> None:
    sample_html = (
        "<html><head><title>Storefront</title><script>console.log('noise')</script></head>"
        "<body><main><h1>ANC Headphones</h1>"
        "<button id='buy' aria-label='Add to Cart'>Add to Cart</button></main></body></html>"
    )
    mesh = BrowserMesh(strict_security=True)
    nav = mesh.navigate("https://example.com/store", html_override=sample_html)
    delta = mesh.snapshot()

    print("Navigation Success:", nav.success)
    print("Token Savings:", f"{delta.token_savings_pct}% (~{delta.estimated_tokens} tokens)")
    print("Anchors:", [a.anchor_id for a in delta.anchors])

    if delta.anchors:
        click_res = mesh.click(delta.anchors[0].anchor_id)
        print("Click Result:", click_res.success, click_res.message)


if __name__ == "__main__":
    main()
