"""AgentBrowserMesh: High-speed, zero-token-waste autonomous browser engine for AI agents."""

__version__ = "1.0.0"

from .core import (
    ActionExecutor,
    ActionResult,
    AnchorRegistry,
    BrowserGuardrails,
    BrowserMesh,
    BrowserSessionState,
    DOMCompiler,
    DOMDelta,
    SecurityVerdict,
    SemanticAnchor,
    create_semantic_anchor,
)
from .serve import BrowserTelemetry, HealthMonitor, HealthSnapshot, MCPServer
from .tools import BenchmarkMatrix, BrowserDoctor, DoctorReport, MatrixRow

__all__ = [
    "BrowserMesh",
    "BrowserSessionState",
    "BrowserGuardrails",
    "SecurityVerdict",
    "DOMCompiler",
    "DOMDelta",
    "SemanticAnchor",
    "AnchorRegistry",
    "create_semantic_anchor",
    "ActionExecutor",
    "ActionResult",
    "MCPServer",
    "HealthMonitor",
    "HealthSnapshot",
    "BrowserTelemetry",
    "BrowserDoctor",
    "DoctorReport",
    "BenchmarkMatrix",
    "MatrixRow",
    "__version__",
]
