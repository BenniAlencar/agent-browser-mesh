"""
Rolling telemetry collector for agent-browser-mesh.
Tracks action latencies (P50/P90/P99), DOM-Delta token savings, and SSRF/injection blocks.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List


def _percentile(sorted_vals: List[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = (len(sorted_vals) - 1) * (pct / 100.0)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


@dataclass
class BrowserActionEvent:
    timestamp: float
    action: str
    latency_ms: float
    success: bool
    blocked: bool
    tokens_saved: int
    savings_pct: float


class BrowserTelemetry:
    """Thread-safe rolling window telemetry for browser mesh sessions."""

    def __init__(self, max_events: int = 1000) -> None:
        self._events: Deque[BrowserActionEvent] = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._total_actions = 0
        self._total_blocked = 0
        self._total_tokens_saved = 0

    def record(
        self,
        action: str,
        latency_ms: float,
        success: bool = True,
        blocked: bool = False,
        tokens_saved: int = 0,
        savings_pct: float = 0.0,
    ) -> None:
        ev = BrowserActionEvent(
            timestamp=time.time(),
            action=action,
            latency_ms=max(0.0, float(latency_ms)),
            success=success,
            blocked=blocked,
            tokens_saved=max(0, int(tokens_saved)),
            savings_pct=max(0.0, min(100.0, float(savings_pct))),
        )
        with self._lock:
            self._events.append(ev)
            self._total_actions += 1
            if blocked:
                self._total_blocked += 1
            self._total_tokens_saved += ev.tokens_saved

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            latencies = sorted(e.latency_ms for e in self._events)
            savings = [e.savings_pct for e in self._events if e.savings_pct > 0]
            total = self._total_actions
            blocked = self._total_blocked
            tokens_saved = self._total_tokens_saved
            window_count = len(self._events)

        avg_savings = (sum(savings) / len(savings)) if savings else 0.0
        return {
            "total_actions": total,
            "window_events": window_count,
            "blocked_count": blocked,
            "tokens_saved_total": tokens_saved,
            "avg_token_savings_pct": round(avg_savings, 2),
            "latency_ms": {
                "p50": round(_percentile(latencies, 50.0), 3),
                "p90": round(_percentile(latencies, 90.0), 3),
                "p99": round(_percentile(latencies, 99.0), 3),
                "mean": round(sum(latencies) / len(latencies), 3) if latencies else 0.0,
            },
        }

    def reset(self) -> None:
        with self._lock:
            self._events.clear()
            self._total_actions = 0
            self._total_blocked = 0
            self._total_tokens_saved = 0
