"""
Deployments Tool — checks recent deployments and their diffs.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List
from app.simulator.telemetry import telemetry_store


def get_recent_deployments(
    service_name: str = None,
    hours: int = 24,
) -> Dict[str, Any]:
    """Get recent deployments, optionally filtered by service."""
    deployments = telemetry_store.get_deployments(service_name=service_name, hours=hours)

    return {
        "service": service_name,
        "time_range_hours": hours,
        "deployments": deployments[:10],
        "total_found": len(deployments),
        "source": "telemetry_store",
    }


def get_deployment_diff(deployment_id: str) -> Dict[str, Any]:
    """Get the diff/changes for a specific deployment."""
    diff = telemetry_store.get_deployment_diff(deployment_id)
    return diff or {"deployment_id": deployment_id, "changes": [], "message": "No diff available"}
