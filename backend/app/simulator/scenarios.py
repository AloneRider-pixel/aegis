"""
Failure Scenarios — predefined incident scenarios for demo and evaluation.
Each scenario generates realistic telemetry and creates an incident.
"""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.simulator.telemetry import telemetry_store


SCENARIOS = {
    "db-connection-exhaustion": {
        "id": "db-connection-exhaustion",
        "name": "Database Connection Exhaustion",
        "description": "A deployment increases DB connections until pool is exhausted",
        "severity": "sev-2",
        "category": "database",
        "service": "checkout-service",
        "symptoms": [
            "HTTP 500 errors increasing",
            "Database connection pool at 100%",
            "Latency spike on checkout endpoints",
        ],
    },
    "api-latency-spike": {
        "id": "api-latency-spike",
        "name": "API Latency Spike",
        "description": "Service latency increases 10x due to memory pressure",
        "severity": "sev-2",
        "category": "performance",
        "service": "api-gateway",
        "symptoms": [
            "P95 latency > 5 seconds",
            "Request timeouts increasing",
            "Memory usage above 90%",
        ],
    },
    "http-500-spike": {
        "id": "http-500-spike",
        "name": "HTTP 500 Error Spike",
        "description": "Error rate spikes after deployment introduces bug",
        "severity": "sev-1",
        "category": "deployment",
        "service": "order-service",
        "symptoms": [
            "Error rate jumped from 0.1% to 25%",
            "All endpoints affected",
            "Started immediately after deployment v2.5.0",
        ],
    },
    "redis-outage": {
        "id": "redis-outage",
        "name": "Redis Cache Outage",
        "description": "Redis becomes unavailable causing cache misses and slowdowns",
        "severity": "sev-2",
        "category": "infrastructure",
        "service": "product-service",
        "symptoms": [
            "Cache hit rate dropped to 0%",
            "Database query rate increased 10x",
            "Response latency increased 5x",
        ],
    },
    "memory-pressure": {
        "id": "memory-pressure",
        "name": "Memory Pressure / OOM",
        "description": "Service consuming excessive memory leading to OOM kills",
        "severity": "sev-2",
        "category": "resource",
        "service": "analytics-service",
        "symptoms": [
            "Memory usage climbing steadily",
            "Pod restarts due to OOMKill",
            "Service intermittently unavailable",
        ],
    },
    "failed-deployment": {
        "id": "failed-deployment",
        "name": "Failed Deployment",
        "description": "New deployment fails health checks and rolls back",
        "severity": "sev-3",
        "category": "deployment",
        "service": "notification-service",
        "symptoms": [
            "Deployment failed health check",
            "Automatic rollback triggered",
            "Brief service disruption",
        ],
    },
    "dependency-timeout": {
        "id": "dependency-timeout",
        "name": "External Dependency Timeout",
        "description": "Payment gateway becomes unresponsive",
        "severity": "sev-1",
        "category": "dependency",
        "service": "payment-service",
        "symptoms": [
            "Payment processing timeouts",
            "Upstream dependency returning 504",
            "Queue depth increasing",
        ],
    },
    "slow-query": {
        "id": "slow-query",
        "name": "Database Slow Query",
        "description": "New query pattern causes table scans and slow responses",
        "severity": "sev-3",
        "category": "database",
        "service": "search-service",
        "symptoms": [
            "Database query latency > 10s",
            "CPU usage spike on DB server",
            "Search response time degraded",
        ],
    },
    "kafka-consumer-lag": {
        "id": "kafka-consumer-lag",
        "name": "Kafka Consumer Lag",
        "description": "Consumer falls behind causing processing delays",
        "severity": "sev-3",
        "category": "messaging",
        "service": "event-processor",
        "symptoms": [
            "Consumer lag increasing",
            "Event processing delayed",
            "Queue depth growing",
        ],
    },
    "cpu-saturation": {
        "id": "cpu-saturation",
        "name": "CPU Saturation",
        "description": "Service CPU usage hits 100% causing throttling",
        "severity": "sev-2",
        "category": "resource",
        "service": "ml-inference-service",
        "symptoms": [
            "CPU usage at 100%",
            "Request processing slowed",
            "Queue backing up",
        ],
    },
    "config-error": {
        "id": "config-error",
        "name": "Incorrect Environment Configuration",
        "description": "Wrong environment config deployed to production",
        "severity": "sev-1",
        "category": "configuration",
        "service": "auth-service",
        "symptoms": [
            "Authentication failures for all users",
            "JWT validation errors",
            "Config points to staging environment",
        ],
    },
    "service-unavailable": {
        "id": "service-unavailable",
        "name": "Service Dependency Unavailable",
        "description": "Critical upstream service goes down completely",
        "severity": "sev-1",
        "category": "dependency",
        "service": "inventory-service",
        "symptoms": [
            "Service returning 503",
            "Health check failing",
            "All dependent services affected",
        ],
    },
}


def get_scenario(scenario_id: str) -> Optional[Dict]:
    return SCENARIOS.get(scenario_id)


def list_scenarios() -> List[Dict]:
    return list(SCENARIOS.values())


def trigger_scenario(scenario_id: str) -> Dict[str, Any]:
    """
    Trigger a failure scenario.
    Generates realistic telemetry and returns incident data.
    """
    scenario = get_scenario(scenario_id)
    if not scenario:
        return {"error": f"Unknown scenario: {scenario_id}"}

    # Reset and activate scenario
    telemetry_store.reset()
    telemetry_store.set_active_scenario(scenario_id)

    service = scenario["service"]
    now = datetime.utcnow()

    # Generate baseline metrics (normal operation)
    for i in range(30):
        ts = now - timedelta(minutes=30 - i)
        telemetry_store.add_metric(service, "request_rate", random.uniform(100, 200), ts)
        telemetry_store.add_metric(service, "error_rate", random.uniform(0.001, 0.01), ts)
        telemetry_store.add_metric(service, "latency_p50", random.uniform(20, 80), ts)
        telemetry_store.add_metric(service, "latency_p95", random.uniform(100, 300), ts)
        telemetry_store.add_metric(service, "cpu_usage", random.uniform(20, 50), ts)
        telemetry_store.add_metric(service, "memory_usage", random.uniform(40, 60), ts)

    # Generate scenario-specific anomaly
    _generate_anomaly(scenario_id, service, now)

    # Generate a deployment if deployment-related
    if scenario["category"] in ("deployment", "configuration"):
        telemetry_store.add_deployment(
            service=service,
            version="v2.5.0",
            status="success",
            changes=["Increased DB connection pool size", "Added new query pattern", "Updated dependencies"],
        )

    # Generate some logs
    _generate_logs(scenario_id, service, now)

    # Generate some traces
    _generate_traces(scenario_id, service, now)

    return {
        "scenario": scenario,
        "service": service,
        "telemetry_generated": True,
        "incident": {
            "title": f"[{scenario['severity'].upper()}] {scenario['name']} — {service}",
            "severity": scenario["severity"],
            "service_name": service,
            "symptoms": scenario["symptoms"],
            "source": "simulator",
        },
    }


def _generate_anomaly(scenario_id: str, service: str, now: datetime):
    """Generate scenario-specific anomaly metrics."""
    for i in range(10):
        ts = now - timedelta(minutes=10 - i)

        if scenario_id == "db-connection-exhaustion":
            telemetry_store.add_metric(service, "db_connections", 80 + i * 2, ts)
            telemetry_store.add_metric(service, "error_rate", 0.01 + i * 0.015, ts)
            telemetry_store.add_metric(service, "latency_p95", 300 + i * 200, ts)
        elif scenario_id == "api-latency-spike":
            telemetry_store.add_metric(service, "latency_p50", 50 + i * 50, ts)
            telemetry_store.add_metric(service, "latency_p95", 200 + i * 500, ts)
            telemetry_store.add_metric(service, "memory_usage", 60 + i * 3.5, ts)
            telemetry_store.add_metric(service, "error_rate", 0.01 + i * 0.02, ts)
        elif scenario_id == "http-500-spike":
            telemetry_store.add_metric(service, "error_rate", 0.01 + i * 0.025, ts)
            telemetry_store.add_metric(service, "request_rate", 150 - i * 5, ts)
        elif scenario_id == "redis-outage":
            telemetry_store.add_metric(service, "cache_hit_rate", 95 - i * 10, ts)
            telemetry_store.add_metric(service, "db_query_rate", 100 + i * 200, ts)
            telemetry_store.add_metric(service, "latency_p95", 200 + i * 300, ts)
        elif scenario_id == "memory-pressure":
            telemetry_store.add_metric(service, "memory_usage", 50 + i * 5, ts)
            telemetry_store.add_metric(service, "pod_restarts", i // 3, ts)
        elif scenario_id == "cpu-saturation":
            telemetry_store.add_metric(service, "cpu_usage", 50 + i * 5, ts)
            telemetry_store.add_metric(service, "latency_p95", 300 + i * 100, ts)
        elif scenario_id == "dependency-timeout":
            telemetry_store.add_metric(service, "upstream_latency", 100 + i * 500, ts)
            telemetry_store.add_metric(service, "error_rate", 0.02 + i * 0.03, ts)
            telemetry_store.add_metric(service, "queue_depth", 10 + i * 50, ts)
        else:
            telemetry_store.add_metric(service, "error_rate", 0.01 + i * 0.02, ts)
            telemetry_store.add_metric(service, "latency_p95", 300 + i * 100, ts)


def _generate_logs(scenario_id: str, service: str, now: datetime):
    """Generate scenario-specific log entries."""
    log_templates = {
        "db-connection-exhaustion": [
            ("ERROR", "Connection pool exhausted: max connections (100) reached"),
            ("ERROR", "Failed to acquire database connection: timeout after 30s"),
            ("ERROR", "checkout-service: database connection pool exhausted"),
            ("WARN", "Connection pool utilization at 95%"),
            ("WARN", "Slow query detected: SELECT * FROM orders WHERE... (12.3s)"),
            ("ERROR", "HTTP 500: Internal server error — database unavailable"),
        ],
        "api-latency-spike": [
            ("ERROR", "Request timeout after 30000ms"),
            ("WARN", "Memory usage at 92% — approaching limit"),
            ("ERROR", "OOM: Container killed by kernel"),
            ("WARN", "GC pause exceeded 500ms"),
            ("ERROR", "HTTP 503: Service temporarily unavailable"),
        ],
        "http-500-spike": [
            ("ERROR", "Unhandled exception in request handler: NullPointerException"),
            ("ERROR", "order-service: failed to process order — null reference"),
            ("ERROR", "Stack trace: at OrderProcessor.process(line 142)"),
            ("ERROR", "HTTP 500: Internal server error"),
        ],
        "redis-outage": [
            ("ERROR", "Redis connection refused: ECONNREFUSED 10.0.1.5:6379"),
            ("WARN", "Cache miss rate at 100%"),
            ("ERROR", "Fallback to database query — cache unavailable"),
            ("WARN", "Database load increasing due to cache misses"),
        ],
        "memory-pressure": [
            ("WARN", "Memory usage at 85%"),
            ("WARN", "Memory usage at 92%"),
            ("ERROR", "OOMKill: container exceeded memory limit"),
            ("WARN", "Pod restarting after OOMKill (restart count: 3)"),
        ],
    }

    templates = log_templates.get(scenario_id, [
        ("ERROR", f"{service}: unexpected error occurred"),
        ("WARN", f"{service}: degraded performance detected"),
    ])

    for i, (level, message) in enumerate(templates * 3):
        ts = now - timedelta(minutes=random.randint(0, 10))
        telemetry_store.add_log(service, level, message, ts)


def _generate_traces(scenario_id: str, service: str, now: datetime):
    """Generate scenario-specific trace spans."""
    operations = {
        "db-connection-exhaustion": [
            ("POST /checkout", 5000, "error"),
            ("db.query:INSERT orders", 12000, "error"),
            ("cache.get:user_session", 2, "ok"),
        ],
        "api-latency-spike": [
            ("GET /api/products", 8000, "error"),
            ("db.query:SELECT products", 7500, "error"),
        ],
        "http-500-spike": [
            ("POST /orders", 100, "error"),
            ("OrderProcessor.process", 50, "error"),
        ],
        "redis-outage": [
            ("GET /products", 3000, "error"),
            ("cache.get:products", 3000, "error"),
            ("db.query:SELECT products", 2800, "ok"),
        ],
    }

    spans = operations.get(scenario_id, [
        ("GET /health", 2000, "error"),
    ])

    for op, duration, status in spans:
        for _ in range(3):
            telemetry_store.add_trace(
                trace_id=uuid.uuid4().hex[:16],
                service=service,
                operation=op,
                duration_ms=duration + random.randint(-100, 100),
                status=status,
            )


import uuid
