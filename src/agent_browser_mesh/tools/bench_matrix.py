"""
Multi-page DOM-Delta token compression and latency benchmark matrix for agent-browser-mesh.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..core.engine import BrowserMesh


@dataclass
class MatrixRow:
    workload: str
    raw_bytes: int
    compact_bytes: int
    savings_pct: float
    anchors_found: int
    latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload": self.workload,
            "raw_bytes": self.raw_bytes,
            "compact_bytes": self.compact_bytes,
            "savings_pct": round(self.savings_pct, 2),
            "anchors_found": self.anchors_found,
            "latency_ms": round(self.latency_ms, 3),
        }


DEFAULT_WORKLOADS: Dict[str, str] = {
    "ecommerce_product": (
        "<!DOCTYPE html><html><head><title>Store</title>"
        "<script>var x=1;</script><style>.p{color:red;}</style></head><body>"
        "<nav><a href='/home'>Home</a><a href='/deals'>Deals</a></nav>"
        "<main><h1>Wireless ANC Headphones</h1><p>40-hour battery life.</p>"
        "<form><input type='number' id='qty' value='1'/>"
        "<button type='submit' aria-label='Add to Cart'>Add to Cart</button></form>"
        "</main><footer>Copyright 2026</footer></body></html>"
    ) * 5,
    "docs_search_page": (
        "<!DOCTYPE html><html><head><title>Docs</title><style>body{margin:0}</style></head><body>"
        "<header><input type='search' placeholder='Search docs' aria-label='Search'/></header>"
        "<main><article><h2>Quickstart</h2><p>Install via pip install agent-browser-mesh.</p>"
        "<a href='/api'>API Reference</a></article></main></body></html>"
    ) * 5,
    "saas_dashboard": (
        "<!DOCTYPE html><html><head><title>Dashboard</title><script>console.log('telemetry')</script></head><body>"
        "<aside><a href='/overview'>Overview</a><a href='/billing'>Billing</a></aside>"
        "<section><h1>Active Nodes</h1><button aria-label='Refresh Nodes'>Refresh</button>"
        "<button aria-label='Deploy Agent'>Deploy</button></section></body></html>"
    ) * 5,
}


class BenchmarkMatrix:
    """Runs reproducible DOM-Delta compaction benchmarks across representative web pages."""

    def run(self, workloads: Optional[Dict[str, str]] = None, reps: int = 3) -> List[MatrixRow]:
        suite = workloads or DEFAULT_WORKLOADS
        reps = max(1, int(reps))
        rows: List[MatrixRow] = []

        for name, html in suite.items():
            total_ms = 0.0
            last_delta = None
            for _ in range(reps):
                mesh = BrowserMesh(strict_security=True)
                t0 = time.perf_counter()
                mesh.navigate(f"https://example.com/{name}", html_override=html)
                last_delta = mesh.snapshot()
                total_ms += (time.perf_counter() - t0) * 1000.0

            assert last_delta is not None
            rows.append(
                MatrixRow(
                    workload=name,
                    raw_bytes=last_delta.raw_size_bytes,
                    compact_bytes=last_delta.compact_size_bytes,
                    savings_pct=last_delta.token_savings_pct,
                    anchors_found=len(last_delta.anchors),
                    latency_ms=total_ms / reps,
                )
            )
        return rows

    @staticmethod
    def format_table(rows: List[MatrixRow]) -> str:
        header = (
            f"{'Workload':<20} | {'Raw Bytes':>10} | {'Compact':>9} | "
            f"{'Savings':>8} | {'Anchors':>7} | {'Latency':>9}"
        )
        sep = "-" * len(header)
        lines = [header, sep]
        for r in rows:
            lines.append(
                f"{r.workload:<20} | {r.raw_bytes:10,d} | {r.compact_bytes:9,d} | "
                f"{r.savings_pct:7.1f}% | {r.anchors_found:7d} | {r.latency_ms:6.2f} ms"
            )
        return "\n".join(lines)
