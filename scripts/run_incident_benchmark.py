"""Run a deterministic failure-simulation benchmark with explicit provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime

from app.simulator.scenarios import SCENARIOS, trigger_scenario
from app.simulator.telemetry import telemetry_store

DEFAULT_SEED = 20260927


def canonical_case(scenario_id: str, result: dict) -> dict:
    reference_time = datetime(2026, 1, 1)
    metrics = telemetry_store.get_metrics(result["service"], time_range_minutes=60, as_of=reference_time)
    logs = telemetry_store.get_logs(service_name=result["service"], time_range_minutes=60, limit=500, as_of=reference_time)
    traces = telemetry_store.get_traces(service_name=result["service"], slow_only=False, time_range_minutes=60, as_of=reference_time)
    deployments = telemetry_store.get_deployments(service_name=result["service"], hours=24, as_of=reference_time)

    return {
        "scenario": scenario_id,
        "severity": result["scenario"]["severity"],
        "service": result["service"],
        "metric_series": {
            name: [round(float(point["value"]), 6) for point in values]
            for name, values in sorted(metrics.items())
        },
        "log_count": len(logs),
        "trace_summary": sorted(
            (trace["operation"], round(float(trace["duration_ms"]), 3), trace["status"])
            for trace in traces
        ),
        "deployment_summary": [
            (deployment["service"], deployment["version"], deployment["status"])
            for deployment in deployments
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic Aegis incident scenarios.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=Path("artifacts/incident-benchmark.json"))
    args = parser.parse_args()

    cases = []
    for scenario_id in sorted(SCENARIOS):
        result = trigger_scenario(scenario_id, seed=args.seed)
        if "error" in result:
            raise SystemExit(result["error"])
        cases.append(canonical_case(scenario_id, result))

    evidence = {
        "evaluation": "deterministic-incident-simulation",
        "seed": args.seed,
        "scenario_count": len(cases),
        "scenarios": cases,
        "commit": os.getenv("GITHUB_SHA"),
    }
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
    evidence["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(
        f"incident benchmark verified: scenarios={len(cases)}, "
        f"seed={args.seed}, sha256={evidence['evidence_sha256']}"
    )


if __name__ == "__main__":
    main()
