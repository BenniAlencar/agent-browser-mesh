"""
Runtime health monitor for agent-browser-mesh.
Validates DOMCompiler, SSRF/prompt-injection guardrails, and semantic anchor registry.
"""

from __future__ import annotations

import platform
import time
from dataclasses import dataclass
from typing import Any, Dict

from ..core.dom_compiler import DOMCompiler
from ..core.guardrails import BrowserGuardrails


@dataclass
class HealthSnapshot:
    status: str  # "healthy" | "degraded" | "unhealthy"
    python_version: str
    platform_system: str
    dom_compiler_ok: bool
    guardrails_ok: bool
    check_latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "python_version": self.python_version,
            "platform_system": self.platform_system,
            "dom_compiler_ok": self.dom_compiler_ok,
            "guardrails_ok": self.guardrails_ok,
            "check_latency_ms": round(self.check_latency_ms, 3),
        }


class HealthMonitor:
    """Performs lightweight runtime health checks for the browser mesh subsystem."""

    def check(self) -> HealthSnapshot:
        t0 = time.perf_counter()

        dom_ok = False
        try:
            compiler = DOMCompiler()
            delta = compiler.compile(
                "<html><head><title>Probe</title></head><body><button>Go</button></body></html>",
                url="https://example.com",
            )
            dom_ok = len(delta.anchors) >= 1
        except Exception:
            dom_ok = False

        guard_ok = False
        try:
            guard = BrowserGuardrails(strict_mode=True)
            blocked = guard.inspect_navigation_url("http://169.254.169.254/latest/meta-data/")
            allowed = guard.inspect_navigation_url("https://example.com")
            guard_ok = (not blocked.allowed) and allowed.allowed
        except Exception:
            guard_ok = False

        status = "healthy" if (dom_ok and guard_ok) else "unhealthy"
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return HealthSnapshot(
            status=status,
            python_version=platform.python_version(),
            platform_system=f"{platform.system()} {platform.release()}",
            dom_compiler_ok=dom_ok,
            guardrails_ok=guard_ok,
            check_latency_ms=elapsed_ms,
        )
