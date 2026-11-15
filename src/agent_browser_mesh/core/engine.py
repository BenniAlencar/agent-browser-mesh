"""BrowserMesh: Sovereign, High-Speed Browser Automation Engine.

Orchestrates:
- Guardrail validation (SSRF, indirect prompt injection)
- Semantic DOM-Delta compilation with 90%+ token reduction
- Deterministic action dispatch via resilient semantic anchors
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

from pydantic import BaseModel, Field

from .guardrails import BrowserGuardrails, SecurityVerdict
from .dom_compiler import DOMCompiler, DOMDelta
from .actions import ActionExecutor, ActionResult
from .fingerprint import SemanticAnchor


class BrowserSessionState(BaseModel):
    """Observable snapshot of the current browser session."""
    current_url: str = Field(default="about:blank")
    title: str = Field(default="")
    is_active: bool = Field(default=True)
    history: List[str] = Field(default_factory=list)
    action_log: List[ActionResult] = Field(default_factory=list)
    security_violations: List[str] = Field(default_factory=list)


class BrowserMesh:
    """The Autonomous Browser Engine for AI Coding Agents."""

    def __init__(self, strict_security: bool = True):
        self.guardrails = BrowserGuardrails(strict_mode=strict_security)
        self.compiler = DOMCompiler()
        self.executor = ActionExecutor(self.compiler.registry)
        self.state = BrowserSessionState()
        self._current_html: str = ""
        self._current_delta: Optional[DOMDelta] = None

    def navigate(self, url: str, html_override: Optional[str] = None) -> ActionResult:
        """Navigates to target URL with pre-execution SSRF and protocol verification."""
        start = time.perf_counter()
        
        # 1. Guardrail inspection
        verdict = self.guardrails.inspect_navigation_url(url)
        if not verdict.allowed:
            self.state.security_violations.extend(verdict.violations)
            elapsed = (time.perf_counter() - start) * 1000.0
            return ActionResult(
                success=False,
                action="navigate",
                value=url,
                message=f"SECURITY_BLOCKED: {verdict.reason}",
                elapsed_ms=round(elapsed, 2),
                metadata={"violations": verdict.violations}
            )

        # 2. Fetch or load content
        raw_html = ""
        if html_override is not None:
            raw_html = html_override
        elif url.startswith("about:"):
            raw_html = "<html><head><title>Blank</title></head><body></body></html>"
        else:
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AgentBrowserMesh/1.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    charset = response.headers.get_content_charset() or "utf-8"
                    raw_html = response.read().decode(charset, errors="replace")
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000.0
                return ActionResult(
                    success=False,
                    action="navigate",
                    value=url,
                    message=f"NETWORK_ERROR: {str(e)}",
                    elapsed_ms=round(elapsed, 2)
                )

        # 3. Guardrail content sanitization (Neutralize indirect prompt injection)
        clean_html, content_verdict = self.guardrails.sanitize_content(raw_html)
        if not content_verdict.allowed:
            self.state.security_violations.extend(content_verdict.violations)

        self._current_html = clean_html
        self.state.current_url = url
        self.state.history.append(url)

        # 4. Compile initial DOM-Delta
        self._current_delta = self.compiler.compile(clean_html, url=url)
        self.state.title = self._current_delta.title

        elapsed = (time.perf_counter() - start) * 1000.0
        result = ActionResult(
            success=True,
            action="navigate",
            value=url,
            message=f"Navigated to '{url}' | Title: '{self.state.title}' | DOM compacted ({self._current_delta.token_savings_pct}% token savings)",
            elapsed_ms=round(elapsed, 2),
            metadata={
                "title": self.state.title,
                "anchors_found": len(self._current_delta.anchors),
                "token_savings_pct": self._current_delta.token_savings_pct,
                "estimated_tokens": self._current_delta.estimated_tokens
            }
        )
        self.state.action_log.append(result)
        return result

    def snapshot(self) -> DOMDelta:
        """Returns the current token-compacted DOM-Delta view."""
        if not self._current_delta:
            self._current_delta = self.compiler.compile(self._current_html, url=self.state.current_url)
        return self._current_delta

    def click(self, target_anchor_id: str) -> ActionResult:
        """Executes a click on an actionable semantic anchor."""
        result = self.executor.execute_click(target_anchor_id)
        self.state.action_log.append(result)
        return result

    def type_text(self, target_anchor_id: str, text: str) -> ActionResult:
        """Enters text into a designated input anchor."""
        result = self.executor.execute_type(target_anchor_id, text)
        self.state.action_log.append(result)
        return result

    def scroll(self, direction: str = "down", amount: int = 500) -> ActionResult:
        """Scrolls the current viewport."""
        result = self.executor.execute_scroll(direction, amount)
        self.state.action_log.append(result)
        return result

    def extract(self, query: str = "") -> Dict[str, Any]:
        """Extracts text content and anchor inventory with zero visual token waste."""
        delta = self.snapshot()
        return {
            "url": self.state.current_url,
            "title": self.state.title,
            "markdown": delta.markdown_view,
            "anchors": [a.model_dump() for a in delta.anchors],
            "estimated_tokens": delta.estimated_tokens,
            "token_savings_pct": delta.token_savings_pct
        }

    def get_security_status(self) -> Dict[str, Any]:
        """Returns security violation ledger and active policies."""
        return {
            "strict_mode": self.guardrails.strict_mode,
            "violations_recorded": self.state.security_violations,
            "is_clean": len(self.state.security_violations) == 0
        }
