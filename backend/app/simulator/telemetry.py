"""
Telemetry Store — in-memory store for simulated metrics, logs, and traces.
In production, this would be backed by Prometheus, Loki, and Tempo.
"""
import threading
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class TelemetryStore:
    """Thread-safe in-memory telemetry store for the failure simulator."""

    def __init__(self):
        self._lock = threading.Lock()
        self._metrics: Dict[str, List[Dict]] = defaultdict(list)
        self._logs: List[Dict] = []
        self._traces: List[Dict] = []
        self._deployments: List[Dict] = []
        self._active_scenario: Optional[str] = None
        self._scenario_start: Optional[datetime] = None

    def reset(self):
        """Clear all telemetry data."""
        with self._lock:
            self._metrics.clear()
            self._logs.clear()
            self._traces.clear()
            self._deployments.clear()
            self._active_scenario = None
            self._scenario_start = None

    # ─── Metrics ───

    def add_metric(self, service: str, metric_name: str, value: float, timestamp: datetime = None):
        ts = timestamp or datetime.utcnow()
        with self._lock:
            self._metrics[f"{service}:{metric_name}"].append({
                "timestamp": ts.isoformat(),
                "value": value,
                "service": service,
                "metric": metric_name,
            })

    def get_metrics(self, service: str, time_range_minutes: int = 30) -> Dict[str, List]:
        cutoff = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        result = {}
        with self._lock:
            for key, entries in self._metrics.items():
                if key.startswith(f"{service}:"):
                    metric_name = key.split(":", 1)[1]
                    filtered = [e for e in entries if datetime.fromisoformat(e["timestamp"]) >= cutoff]
                    if filtered:
                        result[metric_name] = filtered
        return result

    # ─── Logs ───

    def add_log(
        self,
        service: str,
        level: str,
        message: str,
        timestamp: datetime = None,
        trace_id: str = None,
    ):
        ts = timestamp or datetime.utcnow()
        with self._lock:
            self._logs.append({
                "timestamp": ts.isoformat(),
                "service": service,
                "level": level,
                "message": message,
                "trace_id": trace_id or uuid.uuid4().hex[:16],
            })

    def get_logs(
        self,
        service_name: str = None,
        level: str = None,
        query: str = None,
        time_range_minutes: int = 30,
        limit: int = 50,
    ) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        with self._lock:
            results = []
            for log in self._logs:
                ts = datetime.fromisoformat(log["timestamp"])
                if ts < cutoff:
                    continue
                if service_name and log["service"] != service_name:
                    continue
                if level and log["level"] != level:
                    continue
                if query and query.lower() not in log["message"].lower():
                    continue
                results.append(log)
            return results[-limit:]

    # ─── Traces ───

    def add_trace(self, trace_id: str, service: str, operation: str, duration_ms: float, status: str = "ok"):
        with self._lock:
            self._traces.append({
                "trace_id": trace_id,
                "service": service,
                "operation": operation,
                "duration_ms": round(duration_ms, 2),
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
            })

    def get_traces(
        self,
        trace_id: str = None,
        service_name: str = None,
        slow_only: bool = True,
        time_range_minutes: int = 30,
    ) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(minutes=time_range_minutes)
        with self._lock:
            results = []
            for trace in self._traces:
                ts = datetime.fromisoformat(trace["timestamp"])
                if ts < cutoff:
                    continue
                if trace_id and trace["trace_id"] != trace_id:
                    continue
                if service_name and trace["service"] != service_name:
                    continue
                if slow_only and trace["duration_ms"] < 500:
                    continue
                results.append(trace)
            return results

    # ─── Deployments ───

    def add_deployment(self, service: str, version: str, status: str = "success", changes: List[str] = None):
        with self._lock:
            self._deployments.append({
                "deployment_id": uuid.uuid4().hex[:12],
                "service": service,
                "version": version,
                "status": status,
                "changes": changes or [],
                "timestamp": datetime.utcnow().isoformat(),
                "recent": True,
            })

    def get_deployments(self, service_name: str = None, hours: int = 24) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            results = []
            for dep in self._deployments:
                ts = datetime.fromisoformat(dep["timestamp"])
                if ts < cutoff:
                    continue
                if service_name and dep["service"] != service_name:
                    continue
                results.append(dep)
            return results

    def get_deployment_diff(self, deployment_id: str) -> Optional[Dict]:
        with self._lock:
            for dep in self._deployments:
                if dep["deployment_id"] == deployment_id:
                    return {
                        "deployment_id": deployment_id,
                        "service": dep["service"],
                        "version": dep["version"],
                        "changes": dep.get("changes", []),
                    }
            return None

    # ─── Service Health ───

    def get_service_health(self, service: str) -> Optional[Dict]:
        metrics = self.get_metrics(service, time_range_minutes=5)
        if not metrics:
            return None

        error_rates = metrics.get("error_rate", [])
        latest_error = error_rates[-1]["value"] if error_rates else 0

        status = "healthy" if latest_error < 0.05 else ("degraded" if latest_error < 0.15 else "unhealthy")

        return {
            "service": service,
            "status": status,
            "error_rate": latest_error,
            "checks": {
                "http": {"status": "passing" if status != "unhealthy" else "failing"},
                "error_rate": latest_error,
            },
        }

    # ─── Scenario State ───

    def set_active_scenario(self, scenario_id: str):
        with self._lock:
            self._active_scenario = scenario_id
            self._scenario_start = datetime.utcnow()

    def get_active_scenario(self) -> Optional[str]:
        return self._active_scenario


# Global singleton
telemetry_store = TelemetryStore()
