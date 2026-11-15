"""Unit tests for agent_browser_mesh.serve and agent_browser_mesh.tools."""

from agent_browser_mesh import (
    BenchmarkMatrix,
    BrowserDoctor,
    BrowserTelemetry,
    HealthMonitor,
)


def test_browser_telemetry_percentiles_and_reset():
    tel = BrowserTelemetry(max_events=50)
    tel.record("navigate", 15.0, success=True, blocked=False, tokens_saved=900, savings_pct=91.0)
    tel.record("navigate", 1.0, success=False, blocked=True, tokens_saved=0, savings_pct=0.0)
    tel.record("click", 5.0, success=True, blocked=False, tokens_saved=100, savings_pct=89.0)

    snap = tel.snapshot()
    assert snap["total_actions"] == 3
    assert snap["blocked_count"] == 1
    assert snap["tokens_saved_total"] == 1000
    assert snap["latency_ms"]["p50"] == 5.0
    assert snap["avg_token_savings_pct"] == 90.0

    tel.reset()
    assert tel.snapshot()["total_actions"] == 0


def test_health_monitor_reports_healthy():
    snap = HealthMonitor().check()
    data = snap.to_dict()
    assert snap.status == "healthy"
    assert data["dom_compiler_ok"] is True
    assert data["guardrails_ok"] is True


def test_browser_doctor_all_checks_pass():
    report = BrowserDoctor().run()
    assert report.overall_ok is True
    assert len(report.checks) == 4
    assert "ALL CHECKS PASSED" in report.format_report()
    assert report.to_dict()["overall_ok"] is True


def test_benchmark_matrix_runs_workloads():
    bm = BenchmarkMatrix()
    rows = bm.run(reps=1)
    assert len(rows) == 3
    assert all(r.savings_pct > 0 for r in rows)
    table = bm.format_table(rows)
    assert "ecommerce_product" in table
