"""
Metrics Tool — queries the telemetry store for service metrics.
Returns structured data for the agent to analyze.
"""
import random
from datetime import datetime, timedelta
from typing import Any, Dict


def query_metrics(
    service_name: str,
    metric_name: str = "all",
    time_range_minutes: int = 30,
) -> Dict[str, Any]:
    """
    Query metrics for a service.

    In production, this would query Prometheus/OTel.
    Here we use the simulator's telemetry store.

    Returns structured metric data with timestamps and values.
    """
    # Try to get real data from simulator store
    from app.simulator.telemetry import telemetry_store

    data = telemetry_store.get_metrics(service_name, time_range_minutes)

    if data:
        return {
            "service": service_name,
            "time_range_minutes": time_range_minutes,
            "metrics": data,
            "source": "telemetry_store",
        }

    # Fallback: generate realistic baseline metrics
    now = datetime.utcnow()
    metrics = {
        "request_rate": [
            {"timestamp": (now - timedelta(minutes=i)).isoformat(), "value": random.uniform(50, 200)}
            for i in range(time_range_minutes, 0, -1)
        ],
        "error_rate": [
            {"timestamp": (now - timedelta(minutes=i)).isoformat(), "value": random.uniform(0.001, 0.01)}
            for i in range(time_range_minutes, 0, -1)
        ],
        "latency_p50": [
            {"timestamp": (now - timedelta(minutes=i)).isoformat(), "value": random.uniform(20, 80)}
            for i in range(time_range_minutes, 0, -1)
        ],
        "latency_p95": [
            {"timestamp": (now - timedelta(minutes=i)).isoformat(), "value": random.uniform(100, 300)}
            for i in range(time_range_minutes, 0, -1)
        ],
        "cpu_usage": [
            {"timestamp": (now - timedelta(minutes=i)).isoformat(), "value": random.uniform(20, 60)}
            for i in range(time_range_minutes, 0, -1)
        ],
        "memory_usage": [
            {"timestamp": (now - timedelta(minutes=i)).isoformat(), "value": random.uniform(40, 70)}
            for i in range(time_range_minutes, 0, -1)
        ],
    }

    return {
        "service": service_name,
        "time_range_minutes": time_range_minutes,
        "metrics": metrics,
        "source": "baseline_generator",
    }


def get_service_health(service_name: str) -> Dict[str, Any]:
    """Get current health status of a service."""
    from app.simulator.telemetry import telemetry_store

    health = telemetry_store.get_service_health(service_name)
    if health:
        return health

    return {
        "service": service_name,
        "status": "healthy",
        "checks": {
            "http": {"status": "passing", "latency_ms": random.randint(5, 50)},
            "database": {"status": "passing", "latency_ms": random.randint(2, 20)},
            "redis": {"status": "passing", "latency_ms": random.randint(1, 5)},
        },
        "uptime_hours": random.randint(100, 2000),
    }
