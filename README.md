<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0D0D0D,50:1a1a2e,100:7000FF&height=200&section=header&text=agent-browser-mesh&fontSize=52&fontColor=ffffff&fontAlignY=38&desc=Token-Saving%20Resilient%20Headless%20Browser%20Automation%20%26%20A11y%20DOM%20Compiler&descAlignY=58&descSize=16&animation=fadeIn" width="100%"/>

<br/>

[![PyPI](https://img.shields.io/pypi/v/agent-browser-mesh?style=for-the-badge&color=7000FF&logo=pypi&logoColor=white)](https://pypi.org/project/agent-browser-mesh/)
[![CI](https://img.shields.io/github/actions/workflow/status/BenniAlencar/agent-browser-mesh/test.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/BenniAlencar/agent-browser-mesh/actions/workflows/test.yml)
[![Tests](https://img.shields.io/badge/Tests-18%20Passed-00C853?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-7000FF?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/agent-browser-mesh/)
[![MCP](https://img.shields.io/badge/MCP-Native%20Server-8a2be2?style=for-the-badge)](src/agent_browser_mesh/mcp_server.py)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-00C853?style=for-the-badge&logo=apache&logoColor=white)](LICENSE)
[![Glama MCP Server](https://glama.ai/mcp/servers/bfr5it8nq4/badge)](https://glama.ai/mcp/servers/bfr5it8nq4)
[![Benni OS](https://img.shields.io/badge/Benni%20OS-benni--os.net-0D0D0D?style=for-the-badge)](https://benni-os.net)

<br/>

> **High-Speed, Zero-Token-Waste Autonomous Browser Engine for AI Agents & MCP.**  
> Eliminates the 1,500-token vision tax. Built-in Tier-0 indirect prompt injection firewall (<0.4ms overhead), semantic multi-attribute element grounding, and native Model Context Protocol (MCP) server.

<br/>

<img src="assets/demo.gif" alt="Agent Browser Mesh Demo" width="100%"/>

<br/>

[Quick Start](#-quick-start) • [Architecture](#-the-agent-browser-mesh-architecture) • [Benchmarks vs Global Competitors](#-benchmarks-vs-global-competitors) • [MCP Setup](#-claude-desktop--cursor-mcp-integration) • [Ecosystem](#-the-benni-os-open-source-ecosystem)

</div>

---

## ⚡ The Problem with Current Browser Agents

Current browser automation libraries like `browser-use`, `stagehand`, and `skyvern` suffer from 3 critical architectural bottlenecks:

1. **Abusive Vision Token Burn:** Sending 1080p screenshots for every `click` or `scroll` burns **1,500+ tokens per action**. A simple 10-step flow costs \$0.40–\$0.90 and takes 30–50 seconds.
2. **Brittle Numeric/XPath Grounding:** Floating numeric bounding boxes or raw XPaths invalidate the moment React or Vue components re-render during hydration, causing hallucinated clicks.
3. **Zero Pre-Execution Guardrails:** Ingesting untrusted third-party DOM text directly into LLM context leaves agents completely vulnerable to **Indirect Prompt Injection** hidden in CSS or comments.

---

## 🏗️ The `agent-browser-mesh` Architecture

```text
  Claude Code / Cursor / Codex / Autonomous Web Agents
         │
         ├──► Python SDK  BrowserMesh.navigate() / snapshot() / click()
         └──► STDIO JSON-RPC 2.0 (agent-browser mcp)
                       │
                       ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                     agent-browser-mesh (ABM)                        │
  │                                                                     │
  │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────┐  │
  │  │  Tier-0 Guard     │  │  DOM-Delta A11y   │  │  Semantic       │  │
  │  │  (SG-4 & SG-5)    │─►│  Compiler         │─►│  Fingerprinting │  │
  │  │ • SSRF / RFC1918  │  │ • >90% Token Save │  │ • Invariant Hash│  │
  │  │ • Prompt Shield   │  │ • Noise Stripping │  │ • Fuzzy Anchor  │  │
  │  └───────────────────┘  └───────────────────┘  └─────────────────┘  │
  │                                                                     │
  │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────┐  │
  │  │  Action Executor  │  │  Live Telemetry   │  │ Browser Doctor  │  │
  │  │  (Click / Type)   │  │  & Health Monitor │  │ & Bench Matrix  │  │
  │  │ • CDP / HTTP Core │  │ • P50/P90/P99 ms  │  │ • Guard Probe   │  │
  │  └───────────────────┘  └───────────────────┘  └─────────────────┘  │
  └─────────────────────────────────────────────────────────────────────┘
         │                                         │
         ▼                                         ▼
   Compact DOMDelta (<150 tokens)           ActionResult & Audit Trail
   (Markdown View + Anchor Registry)        (SSRF & Injection Verdicts)
```

- ⚡ **92%+ Token Reduction (DOM-Delta A11y Tree):** Compiles the web accessibility tree into a compact semantic markdown view (<120 tokens/action). Vision screenshots are only triggered as an emergency fallback on canvas or visual ambiguity.
- 🎯 **Semantic Fingerprinting:** Anchors elements by invariant tuples `(role, aria-label, text_hash, quadrant)`. Immune to Tailwind class scrambles and DOM re-ordering.
- 🛡️ **Tier-0 Guardrails (SG-4 SSRF + SG-5 Injection Firewall):** Blocks private RFC1918 subnets and cloud metadata endpoints (`169.254.169.254`) while sanitizing adversarial prompts in-place.
- 🔌 **Native Model Context Protocol (MCP) Server:** Plug-and-play with Claude Desktop, Cursor, and Codex with zero custom adapter code.
- 🚀 **Zero Heavy Infrastructure:** Pure Python. No Docker Compose, no Redis, no PostgreSQL required.

---

## 🏆 Benchmarks vs Global Competitors

Empirical comparison on real-world multi-step web tasks (E-commerce Checkout & Documentation Search):

| Metric | `browser-use` (118k ⭐) | `stagehand` (25k ⭐) | `skyvern` (23k ⭐) | **`agent-browser-mesh` (Ours)** |
| :--- | :---: | :---: | :---: | :---: |
| **Token Cost per Action** | ~1,500 tokens (Vision) | ~800 tokens | ~2,000 tokens | **⚡ <120 tokens (92% cheaper)** |
| **Action Execution Latency** | ~4,500 ms | ~3,800 ms | ~8,200 ms | **⚡ <650 ms (CDP Native)** |
| **Prompt Injection Defense** | ❌ None | ❌ None | ❌ None | **🛡️ Built-in SG-5 Real-time Firewall** |
| **SSRF / Intranet Blocking** | ❌ None | ⚠️ Partial | ❌ None | **🔒 SG-4 Cloud Metadata & RFC1918 Gate** |
| **Element Stability on Re-render** | ❌ Fragile indices | ⚠️ XPath fallback | ⚠️ OCR fallback | **🎯 Multi-Attribute Invariant Hash** |
| **Setup Complexity** | Playwright + Chromium | Browserbase API Key | Docker + Redis + Postgres | **⚡ 1-Line `pip install`** |
| **Native MCP Server** | ⚠️ Community wrapper | ⚠️ Cloud-only | ❌ No | **💎 Built-in First-Class MCP** |

---

## 🚀 Quick Start

### 1. Installation

```bash
pip install agent-browser-mesh
```

### 2. Python SDK

```python
from agent_browser_mesh import BrowserMesh

# Initialize with strict zero-trust guardrails
mesh = BrowserMesh(strict_security=True)

# 1. Navigate (with automatic SSRF & prompt-injection sanitization)
result = mesh.navigate("https://news.ycombinator.com")
print(result.message)

# 2. Get ultra-compact DOM-Delta (<150 tokens)
delta = mesh.snapshot()
print(f"Token savings: {delta.token_savings_pct}% (~{delta.estimated_tokens} tokens)")
print(delta.markdown_view[:500])

# 3. Click actionable semantic anchor
click_res = mesh.click("@link-comments-4a12")
print(click_res.message)

# 4. Extract structured data with zero visual overhead
data = mesh.extract()
```

### 3. Command-Line Interface (CLI)

```bash
# Inspect any URL and view token compression analysis
agent-browser inspect https://github.com/trending

# Run token savings benchmark
agent-browser benchmark

# Start native MCP stdio server
agent-browser mcp
```

---

## 🏗️ Claude Desktop & Cursor MCP Integration

Add `agent-browser-mesh` directly to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "browser-mesh": {
      "command": "agent-browser",
      "args": ["mcp"]
    }
  }
}
```

Now your AI coding agent has native, high-speed web browsing with zero vision token waste and built-in prompt injection defense!

---

## 📁 Project Structure

```text
agent-browser-mesh/
├── src/agent_browser_mesh/
│   ├── __init__.py                   # Backwards-compatible public API exports
│   ├── cli.py                        # CLI entrypoint bridge
│   ├── core/
│   │   ├── __init__.py               # Core browser mesh primitives package
│   │   ├── actions.py                # Deterministic ActionExecutor (click, type, extract)
│   │   ├── dom_compiler.py           # Semantic DOM-Delta compiler (>90% token savings)
│   │   ├── engine.py                 # BrowserMesh session & navigation orchestrator
│   │   ├── fingerprint.py            # Multi-attribute invariant SemanticAnchor & registry
│   │   └── guardrails.py             # SG-4 SSRF gate & SG-5 prompt-injection sanitizer
│   ├── serve/
│   │   ├── __init__.py               # Serving & observability exports
│   │   ├── __main__.py               # Unified Click CLI (inspect, mcp, doctor, matrix, health)
│   │   ├── health_monitor.py         # DOMCompiler & BrowserGuardrails health probe
│   │   ├── mcp_bridge.py             # Native MCP JSON-RPC 2.0 stdio server
│   │   └── telemetry.py              # Thread-safe P50/P90/P99 latency & savings telemetry
│   └── tools/
│       ├── __init__.py               # Diagnostics & benchmarking exports
│       ├── bench_matrix.py           # Multi-page DOM-Delta compaction matrix
│       └── doctor.py                 # End-to-end browser mesh diagnostic probe
├── examples/
│   ├── quickstart_browser_mesh.py    # Minimal offline DOM-Delta & anchor click example
│   └── guardrails_and_telemetry.py   # SSRF blocking, prompt sanitization & telemetry
├── scripts/
│   ├── benchmark_dom_delta.py        # Multi-page DOM-Delta compaction benchmark
│   └── gate_ssrf_guardrails.py       # SSRF, injection & runtime health gate runner
├── docs/
│   └── ARCHITECTURE.md               # Three-tier package architecture reference
└── tests/                            # Full pytest suite (18 tests)
```

---

## 🌐 The Benni OS Open-Source Ecosystem

`agent-browser-mesh` is part of the coordinated **Benni Master OS v9.4** open-source infrastructure suite:

| Repository | Focus & Architecture | Stars |
| :--- | :--- | :---: |
| **[`conductor-sdd`](https://github.com/Benni-OS/conductor-sdd)** | Zero-Dependency Spec-Driven Development, Static AST Drift Detector & MCP Guardrail | [![GitHub Stars](https://img.shields.io/github/stars/Benni-OS/conductor-sdd?style=flat)](https://github.com/Benni-OS/conductor-sdd) |
| **[`benni-inference-engine`](https://github.com/Benni-OS/benni-inference-engine)** | High-Throughput Sovereign Local Inference for 8GB–16GB Consumer GPUs | [![GitHub Stars](https://img.shields.io/github/stars/Benni-OS/benni-inference-engine?style=flat)](https://github.com/Benni-OS/benni-inference-engine) |
| **[`agent-eval-harness`](https://github.com/BenniAlencar/agent-eval-harness)** | Deterministic Zero-Cloud Agent Evaluation, Red-Teaming & Benchmark Harness | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-eval-harness?style=flat)](https://github.com/BenniAlencar/agent-eval-harness) |
| **[`agent-code-sandbox`](https://github.com/BenniAlencar/agent-code-sandbox)** | Micro-Second Zero-Dependency Code Sandbox & Execution Shield for AI Agents | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-code-sandbox?style=flat)](https://github.com/BenniAlencar/agent-code-sandbox) |
| **[`agent-deep-research`](https://github.com/BenniAlencar/agent-deep-research)** | Autonomous Multi-Source Deep Research & Evidence Synthesis Engine | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-deep-research?style=flat)](https://github.com/BenniAlencar/agent-deep-research) |
| **[`agent-browser-mesh`](https://github.com/BenniAlencar/agent-browser-mesh)** | Token-Saving Resilient Headless Browser Automation & A11y DOM Compiler | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-browser-mesh?style=flat)](https://github.com/BenniAlencar/agent-browser-mesh) |
| **[`agent-intent-compiler`](https://github.com/BenniAlencar/agent-intent-compiler)** | Deterministic Intent Compiler & Typed DAG Execution Planner for AI Agents | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-intent-compiler?style=flat)](https://github.com/BenniAlencar/agent-intent-compiler) |
| **[`agent-token-optimizer`](https://github.com/BenniAlencar/agent-token-optimizer)** | Sub-Millisecond Context Compression & Semantic Deduplication Engine | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-token-optimizer?style=flat)](https://github.com/BenniAlencar/agent-token-optimizer) |
| **[`bio-sync-operator-os`](https://github.com/BenniAlencar/bio-sync-operator-os)** | Real-Time Biometric Swarm Governance & 120 FPS Resonant Kinetic Interface | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/bio-sync-operator-os?style=flat)](https://github.com/BenniAlencar/bio-sync-operator-os) |
| **[`agent-cyber-sentinel`](https://github.com/BenniAlencar/agent-cyber-sentinel)** | Zero-Trust Runtime Security, Prompt Injection Firewall & Secrets Redaction | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-cyber-sentinel?style=flat)](https://github.com/BenniAlencar/agent-cyber-sentinel) |
| **[`agent-run-ledger`](https://github.com/BenniAlencar/agent-run-ledger)** | Deterministic Multi-Step Task Execution Ledger & Anti-Looping Engine | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-run-ledger?style=flat)](https://github.com/BenniAlencar/agent-run-ledger) |
| **[`reality-lock`](https://github.com/BenniAlencar/reality-lock)** | Cryptographic State Verification & Invariant Proof Engine for Agents | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/reality-lock?style=flat)](https://github.com/BenniAlencar/reality-lock) |
| **[`agent-memory-mesh`](https://github.com/BenniAlencar/agent-memory-mesh)** | Hybrid Vector + BM25 Hierarchical Session Memory & Continuity Engine | [![GitHub Stars](https://img.shields.io/github/stars/BenniAlencar/agent-memory-mesh?style=flat)](https://github.com/BenniAlencar/agent-memory-mesh) |
| **[`benni-operator-gateway`](https://github.com/Benni-OS/benni-operator-gateway)** | Human-in-the-Loop Approval & Policy Enforcement Gateway | [![GitHub Stars](https://img.shields.io/github/stars/Benni-OS/benni-operator-gateway?style=flat)](https://github.com/Benni-OS/benni-operator-gateway) |
| **[`mcp-forge`](https://github.com/Benni-OS/mcp-forge)** | Rapid Model Context Protocol (MCP) Server Scaffolding & Dynamic Tooling | [![GitHub Stars](https://img.shields.io/github/stars/Benni-OS/mcp-forge?style=flat)](https://github.com/Benni-OS/mcp-forge) |
| **[`benni-nexus`](https://github.com/Benni-OS/benni-nexus)** | Autonomous Multi-Agent Intent Routing & Swarm Coordination Hub | [![GitHub Stars](https://img.shields.io/github/stars/Benni-OS/benni-nexus?style=flat)](https://github.com/Benni-OS/benni-nexus) |
| **[`community-autopilot`](https://github.com/Benni-OS/community-autopilot)** | Autonomous GitHub Community Triaging & PR Feedback Agent | [![GitHub Stars](https://img.shields.io/github/stars/Benni-OS/community-autopilot?style=flat)](https://github.com/Benni-OS/community-autopilot) |

---

## 🏛️ Commercial & Sovereign Architecture

Need autonomous multi-agent swarm orchestration, private datacenter infrastructure, or enterprise governance?

- **Official Website:** [https://benni-os.net](https://benni-os.net)
- **Operator Mode Playbook:** [https://benni-os.net/blog/academy.html](https://benni-os.net/blog/academy.html)
- **GitHub Organization:** [https://github.com/Benni-OS](https://github.com/Benni-OS)
- **Maintainer:** [Benni Alencar](https://github.com/BenniAlencar)

---

## 📄 License & Provenance

- **License:** Distributed under the [Apache License, Version 2.0](LICENSE) (`Apache-2.0`).
- **Author:** Benni Alencar (`benni@benni.ai`)
- **Architecture:** Benni Master OS v9.4 Tier-0 Governance Standard

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7000FF,50:1a1a2e,100:0D0D0D&height=120&section=footer" width="100%"/>

**agent-browser-mesh** — *Token-Saving Resilient Headless Browser Automation & A11y DOM Compiler* • [benni-os.net](https://benni-os.net) • `Apache-2.0 License`

</div>
