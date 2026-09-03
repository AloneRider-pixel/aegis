"""
Traces Tool — inspects distributed traces for latency analysis.
"""
from typing import Any, Dict
from app.simulator.telemetry import telemetry_store


def inspect_trace(
    trace_id: str = None,
    service_name: str = None,
    slow_only: bool = True,
    time_range_minutes: int = 30,
) -> Dict[str, Any]:
    """
    Inspect traces for a service or specific trace ID.
    Identifies slow spans and error spans.
    """
    traces = telemetry_store.get_traces(
        trace_id=trace_id,
        service_name=service_name,
        slow_only=slow_only,
        time_range_minutes=time_range_minutes,
    )

    return {
        "trace_id": trace_id,
        "service": service_name,
        "traces": traces[:10],
        "total_found": len(traces),
        "source": "telemetry_store",
    }
