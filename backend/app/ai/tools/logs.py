"""
Logs Tool — searches the telemetry log store.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List


def search_logs(
    service_name: str = None,
    level: str = None,
    query: str = None,
    time_range_minutes: int = 30,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Search logs for relevant entries.

    In production, queries Loki/Elasticsearch.
    Here uses the simulator's telemetry store.
    """
    from app.simulator.telemetry import telemetry_store

    logs = telemetry_store.get_logs(
        service_name=service_name,
        level=level,
        query=query,
        time_range_minutes=time_range_minutes,
        limit=limit,
    )

    if logs:
        return {
            "query": query,
            "service": service_name,
            "level": level,
            "time_range_minutes": time_range_minutes,
            "logs": logs[:limit],
            "total_found": len(logs),
            "source": "telemetry_store",
        }

    return {
        "query": query,
        "service": service_name,
        "logs": [],
        "total_found": 0,
        "source": "telemetry_store",
        "message": "No logs found matching criteria",
    }
