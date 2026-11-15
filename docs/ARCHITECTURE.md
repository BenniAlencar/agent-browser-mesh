# Architecture — `agent-browser-mesh`

`agent-browser-mesh` follows the **Benni Master OS v9.4** modular three-tier package layout:

1. **`core/` (Browser Engine, DOM-Delta & Guardrails)**
   - `guardrails.py`: Tier-0 SSRF gate (blocks RFC1918 subnets, `169.254.169.254`, `file://`/`javascript:`) and real-time indirect prompt-injection sanitizer.
   - `dom_compiler.py`: Semantic DOM-Delta compiler stripping `<script>`/`<style>`/boilerplate into compact markdown (<150 tokens).
   - `fingerprint.py`: Multi-attribute invariant `SemanticAnchor` hashing `(role, aria-label, text_hash, quadrant)` and `AnchorRegistry`.
   - `actions.py`: Deterministic `ActionExecutor` for anchor-based clicks, typing, and extraction.
   - `engine.py`: `BrowserMesh` orchestrating navigation, snapshots, and session state.

2. **`serve/` (Runtime Interfaces & Observability)**
   - `mcp_bridge.py`: Native JSON-RPC 2.0 stdio Model Context Protocol server (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_extract`, `browser_security_status`).
   - `telemetry.py`: Thread-safe rolling P50/P90/P99 action latency, block count, and token-savings collector.
   - `health_monitor.py`: Runtime health probe verifying `DOMCompiler` and `BrowserGuardrails` readiness.
   - `__main__.py`: Unified Click CLI entrypoint (`inspect`, `mcp`, `benchmark`, `doctor`, `matrix`, `health`).

3. **`tools/` (Diagnostics & Benchmarks)**
   - `doctor.py`: End-to-end diagnostic probe (`BrowserDoctor`) with structured JSON and human-readable reports.
   - `bench_matrix.py`: Multi-page DOM-Delta compaction & latency matrix (`BenchmarkMatrix`).
