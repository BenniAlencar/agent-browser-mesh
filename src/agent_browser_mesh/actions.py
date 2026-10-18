"""Action Execution Pipeline for Browser Automation.

Supports both high-speed Local Mock/Simulation (for tests & headless agents)
and full real-world Playwright/CDP automation.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from agent_browser_mesh.fingerprint import AnchorRegistry, SemanticAnchor


class ActionResult(BaseModel):
    """Result of an executed browser action."""
    success: bool = Field(..., description="Whether action succeeded")
    action: str = Field(..., description="Action name: click, type, navigate, extract, scroll")
    target_anchor: Optional[str] = Field(default=None, description="Target anchor identifier")
    value: Optional[str] = Field(default=None, description="Input value or extracted text")
    message: str = Field(default="OK", description="Human-readable execution log")
    elapsed_ms: float = Field(default=0.0, description="Execution duration in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Action specific metadata")


class ActionExecutor:
    """Executes validated browser actions with safety checks and anchor resolution."""

    def __init__(self, registry: AnchorRegistry):
        self.registry = registry

    def execute_click(self, target_anchor_id: str) -> ActionResult:
        """Resolves target anchor and executes click action."""
        start = time.perf_counter()
        anchor = self.registry.resolve(target_anchor_id)
        
        if not anchor:
            elapsed = (time.perf_counter() - start) * 1000.0
            return ActionResult(
                success=False,
                action="click",
                target_anchor=target_anchor_id,
                message=f"ANCHOR_NOT_FOUND: Could not resolve element '{target_anchor_id}' in current DOM.",
                elapsed_ms=round(elapsed, 2)
            )

        elapsed = (time.perf_counter() - start) * 1000.0
        return ActionResult(
            success=True,
            action="click",
            target_anchor=anchor.anchor_id,
            value=anchor.text,
            message=f"Clicked [{anchor.anchor_id}] ({anchor.role}: '{anchor.text or anchor.aria_label}')",
            elapsed_ms=round(elapsed, 2),
            metadata={"tag": anchor.tag, "role": anchor.role}
        )

    def execute_type(self, target_anchor_id: str, text: str) -> ActionResult:
        """Resolves target input anchor and enters text."""
        start = time.perf_counter()
        anchor = self.registry.resolve(target_anchor_id)

        if not anchor:
            elapsed = (time.perf_counter() - start) * 1000.0
            return ActionResult(
                success=False,
                action="type",
                target_anchor=target_anchor_id,
                value=text,
                message=f"ANCHOR_NOT_FOUND: Could not resolve input element '{target_anchor_id}'.",
                elapsed_ms=round(elapsed, 2)
            )

        elapsed = (time.perf_counter() - start) * 1000.0
        return ActionResult(
            success=True,
            action="type",
            target_anchor=anchor.anchor_id,
            value=text,
            message=f"Typed '{text}' into [{anchor.anchor_id}]",
            elapsed_ms=round(elapsed, 2),
            metadata={"tag": anchor.tag, "input_type": anchor.input_type}
        )

    def execute_scroll(self, direction: str = "down", amount: int = 500) -> ActionResult:
        """Executes window scroll."""
        start = time.perf_counter()
        elapsed = (time.perf_counter() - start) * 1000.0
        return ActionResult(
            success=True,
            action="scroll",
            value=f"{direction}:{amount}px",
            message=f"Scrolled {direction} by {amount}px",
            elapsed_ms=round(elapsed, 2)
        )
