"""
Investigation Agent — LangGraph state machine for incident investigation.

Flow:
  START → UNDERSTAND → COLLECT_EVIDENCE → ANALYZE → HYPOTHESIZE →
  VALIDATE → ROOT_CAUSE → REMEDIATION → [HUMAN_APPROVAL] → VERIFY → POSTMORTEM
"""
import logging
from datetime import datetime
from typing import Dict

from langgraph.graph import END, START, StateGraph

from app.ai.agent.state import AgentState
from app.ai.tools.metrics import query_metrics
from app.ai.tools.logs import search_logs
from app.ai.tools.traces import inspect_trace
from app.ai.tools.deployments import get_recent_deployments
from app.ai.tools.runbooks import search_runbook, search_previous_incidents

logger = logging.getLogger(__name__)


# ─── Node Functions ───

async def understand_incident(state: AgentState) -> Dict:
    """Parse incident details and identify initial investigation direction."""
    trace_entry = {
        "phase": "understand_incident",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "analyzing incident symptoms",
        "details": {
            "title": state["incident_title"],
            "severity": state["severity"],
            "symptoms": state["symptoms"],
        },
    }

    return {
        "current_phase": "collect_evidence",
        "investigation_trace": state.get("investigation_trace", []) + [trace_entry],
        "iteration": state.get("iteration", 0) + 1,
    }


async def collect_evidence(state: AgentState) -> Dict:
    """Gather metrics, logs, traces, and deployment data."""
    service = state.get("service_name", "unknown")
    trace = state.get("investigation_trace", [])

    # Query metrics
    metrics = query_metrics(service_name=service, time_range_minutes=30)

    # Search logs for errors
    logs = search_logs(
        service_name=service,
        level="error",
        time_range_minutes=30,
        limit=20,
    )

    # Check traces
    traces = inspect_trace(service_name=service, slow_only=True)

    # Check recent deployments
    deployments = get_recent_deployments(service_name=service, hours=24)

    tool_calls = state.get("tool_calls", [])
    tool_calls.extend([
        {"tool": "query_metrics", "service": service, "result_count": len(metrics.get("metrics", {}))},
        {"tool": "search_logs", "service": service, "result_count": len(logs.get("logs", []))},
        {"tool": "inspect_trace", "service": service, "result_count": len(traces.get("traces", []))},
        {"tool": "get_recent_deployments", "service": service, "result_count": len(deployments.get("deployments", []))},
    ])

    trace.append({
        "phase": "collect_evidence",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "gathered telemetry data",
        "tools_called": ["query_metrics", "search_logs", "inspect_trace", "get_recent_deployments"],
    })

    return {
        "current_phase": "analyze",
        "metrics_data": metrics.get("metrics", {}),
        "logs_data": logs.get("logs", []),
        "traces_data": traces.get("traces", []),
        "deployment_data": deployments.get("deployments", []),
        "tool_calls": tool_calls,
        "investigation_trace": trace,
        "iteration": state.get("iteration", 0) + 1,
    }


async def analyze_evidence(state: AgentState) -> Dict:
    """Analyze collected evidence, search runbooks and history."""
    service = state.get("service_name", "unknown")
    symptoms = state.get("symptoms", [])
    logs = state.get("logs_data", [])
    metrics = state.get("metrics_data", {})
    trace = state.get("investigation_trace", [])

    # Build query from symptoms and log patterns
    error_keywords = []
    for log in logs[:5]:
        msg = log.get("message", "")
        if "error" in msg.lower() or "fail" in msg.lower():
            error_keywords.append(msg[:100])

    query = " ".join(symptoms[:3] + error_keywords[:2])

    # Search runbooks
    runbooks = search_runbook(query=query or "incident investigation", service=service)

    # Search similar past incidents
    history = search_previous_incidents(query=query or "service incident", top_k=3)

    tool_calls = state.get("tool_calls", [])
    tool_calls.extend([
        {"tool": "search_runbook", "query": query[:100], "results": len(runbooks.get("results", []))},
        {"tool": "search_previous_incidents", "query": query[:100], "results": len(history.get("results", []))},
    ])

    trace.append({
        "phase": "analyze",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "searched knowledge base and incident history",
        "tools_called": ["search_runbook", "search_previous_incidents"],
    })

    return {
        "current_phase": "hypothesize",
        "runbook_results": runbooks.get("results", []),
        "historical_incidents": history.get("results", []),
        "tool_calls": tool_calls,
        "investigation_trace": trace,
        "iteration": state.get("iteration", 0) + 1,
    }


async def form_hypotheses(state: AgentState) -> Dict:
    """Form root-cause hypotheses from evidence."""
    symptoms = state.get("symptoms", [])
    logs = state.get("logs_data", [])
    metrics = state.get("metrics_data", {})
    deployments = state.get("deployment_data", [])
    runbooks = state.get("runbook_results", [])
    trace = state.get("investigation_trace", [])

    hypotheses = []

    # Check for deployment-related issues
    recent_deps = [d for d in deployments if d.get("recent", False)]
    if recent_deps:
        dep = recent_deps[0]
        hypotheses.append({
            "hypothesis": f"Deployment {dep.get('version', 'unknown')} introduced a regression",
            "confidence": 0.7,
            "evidence": [
                f"Deployment to {dep.get('service', 'unknown')} at {dep.get('timestamp', 'unknown')}",
                f"Version: {dep.get('version', 'unknown')}",
            ],
            "type": "deployment",
        })

    # Check for error patterns in logs
    error_patterns = {}
    for log in logs:
        msg = log.get("message", "").lower()
        if "connection" in msg and ("pool" in msg or "exhaust" in msg or "refused" in msg):
            error_patterns["database_connection"] = error_patterns.get("database_connection", 0) + 1
        elif "timeout" in msg:
            error_patterns["timeout"] = error_patterns.get("timeout", 0) + 1
        elif "memory" in msg or "oom" in msg:
            error_patterns["memory"] = error_patterns.get("memory", 0) + 1
        elif "rate limit" in msg or "throttl" in msg:
            error_patterns["rate_limit"] = error_patterns.get("rate_limit", 0) + 1

    if error_patterns.get("database_connection", 0) >= 3:
        hypotheses.append({
            "hypothesis": "Database connection pool exhaustion",
            "confidence": 0.85,
            "evidence": [f"{error_patterns['database_connection']} connection-related errors in logs"],
            "type": "database",
        })

    if error_patterns.get("timeout", 0) >= 3:
        hypotheses.append({
            "hypothesis": "Upstream service timeout causing cascading failures",
            "confidence": 0.75,
            "evidence": [f"{error_patterns['timeout']} timeout errors detected"],
            "type": "dependency",
        })

    if error_patterns.get("memory", 0) >= 2:
        hypotheses.append({
            "hypothesis": "Memory pressure / OOM kills",
            "confidence": 0.8,
            "evidence": [f"{error_patterns['memory']} memory-related errors in logs"],
            "type": "resource",
        })

    # Check runbook matches
    for rb in runbooks[:2]:
        if rb.get("relevance_score", 0) > 0.7:
            hypotheses.append({
                "hypothesis": f"Matches runbook: {rb.get('title', 'unknown')}",
                "confidence": rb.get("relevance_score", 0.5),
                "evidence": [f"Runbook match: {rb.get('title', '')} (score: {rb.get('relevance_score', 0):.2f})"],
                "type": "runbook_match",
            })

    # Default hypothesis if none formed
    if not hypotheses:
        hypotheses.append({
            "hypothesis": "Insufficient evidence to determine root cause",
            "confidence": 0.3,
            "evidence": ["No clear patterns detected in available telemetry"],
            "type": "unknown",
        })

    # Sort by confidence
    hypotheses.sort(key=lambda x: x["confidence"], reverse=True)

    trace.append({
        "phase": "hypothesize",
        "timestamp": datetime.utcnow().isoformat(),
        "action": f"formed {len(hypotheses)} hypotheses",
        "hypotheses_count": len(hypotheses),
        "top_hypothesis": hypotheses[0]["hypothesis"] if hypotheses else None,
    })

    return {
        "current_phase": "validate",
        "hypotheses": hypotheses,
        "root_cause": hypotheses[0]["hypothesis"] if hypotheses else None,
        "confidence": hypotheses[0]["confidence"] if hypotheses else 0.0,
        "investigation_trace": trace,
        "iteration": state.get("iteration", 0) + 1,
    }


async def validate_hypothesis(state: AgentState) -> Dict:
    """Validate the top hypothesis against additional evidence."""
    hypotheses = state.get("hypotheses", [])
    logs = state.get("logs_data", [])
    metrics = state.get("metrics_data", {})
    trace = state.get("investigation_trace", [])

    if not hypotheses:
        return {
            "current_phase": "recommend",
            "root_cause": "Insufficient evidence to determine root cause. Additional investigation required.",
            "confidence": 0.1,
            "investigation_trace": trace + [{
                "phase": "validate",
                "timestamp": datetime.utcnow().isoformat(),
                "action": "no hypotheses to validate",
            }],
            "iteration": state.get("iteration", 0) + 1,
        }

    top = hypotheses[0]
    validated = True
    additional_evidence = []

    # Validate based on type
    if top["type"] == "deployment":
        recent_deps = [d for d in state.get("deployment_data", []) if d.get("recent")]
        if recent_deps:
            additional_evidence.append(f"Confirmed: recent deployment {recent_deps[0].get('version')} found")
        else:
            validated = False
            additional_evidence.append("No recent deployments found to confirm")

    elif top["type"] == "database":
        db_errors = sum(1 for l in logs if "connection" in l.get("message", "").lower() and ("pool" in l.get("message", "").lower() or "exhaust" in l.get("message", "").lower()))
        if db_errors >= 2:
            additional_evidence.append(f"Confirmed: {db_errors} database connection errors")
        else:
            validated = False
            additional_evidence.append("Insufficient database errors to confirm")

    elif top["type"] == "memory":
        additional_evidence.append("Memory pressure pattern detected in logs")

    evidence_chain = state.get("evidence_chain", [])
    evidence_chain.extend([{"type": "validation", "finding": e} for e in additional_evidence])

    trace.append({
        "phase": "validate",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "validated hypothesis",
        "hypothesis": top["hypothesis"],
        "validated": validated,
        "additional_evidence": additional_evidence,
    })

    return {
        "current_phase": "recommend",
        "evidence_chain": evidence_chain,
        "investigation_trace": trace,
        "iteration": state.get("iteration", 0) + 1,
    }


async def recommend_remediation(state: AgentState) -> Dict:
    """Generate remediation recommendation based on root cause."""
    root_cause = state.get("root_cause", "")
    hypotheses = state.get("hypotheses", [])
    service = state.get("service_name", "unknown")
    trace = state.get("investigation_trace", [])

    remediation = None

    if "deployment" in root_cause.lower() or (hypotheses and hypotheses[0].get("type") == "deployment"):
        remediation = {
            "action": "rollback_deployment",
            "description": f"Rollback {service} to previous stable version",
            "parameters": {"service": service, "action": "rollback"},
            "risk": "low",
            "rollback_strategy": "Re-deploy the failed version if rollback causes issues",
            "expected_impact": "Restore service to pre-deployment state",
            "requires_approval": True,
        }
    elif "database" in root_cause.lower() or "connection" in root_cause.lower():
        remediation = {
            "action": "scale_connection_pool",
            "description": f"Increase database connection pool for {service} and restart",
            "parameters": {"service": service, "action": "restart", "pool_size": "increase_50_percent"},
            "risk": "low",
            "rollback_strategy": "Revert pool size configuration",
            "expected_impact": "Resolve connection exhaustion",
            "requires_approval": True,
        }
    elif "memory" in root_cause.lower():
        remediation = {
            "action": "restart_service",
            "description": f"Restart {service} to clear memory pressure",
            "parameters": {"service": service, "action": "restart"},
            "risk": "medium",
            "rollback_strategy": "No rollback needed — restart is idempotent",
            "expected_impact": "Clear memory and restore service",
            "requires_approval": True,
        }
    else:
        remediation = {
            "action": "investigate_manually",
            "description": "Insufficient confidence for automated remediation. Manual investigation recommended.",
            "parameters": {},
            "risk": "none",
            "rollback_strategy": "N/A",
            "expected_impact": "N/A",
            "requires_approval": False,
        }

    trace.append({
        "phase": "recommend",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "generated remediation recommendation",
        "remediation_action": remediation["action"],
        "requires_approval": remediation["requires_approval"],
    })

    return {
        "current_phase": "complete",
        "recommended_remediation": remediation,
        "investigation_trace": trace,
        "iteration": state.get("iteration", 0) + 1,
    }


# ─── Build the Graph ───

def build_investigation_graph() -> StateGraph:
    """Build and compile the investigation state machine."""

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("understand_incident", understand_incident)
    graph.add_node("collect_evidence", collect_evidence)
    graph.add_node("analyze_evidence", analyze_evidence)
    graph.add_node("form_hypotheses", form_hypotheses)
    graph.add_node("validate_hypothesis", validate_hypothesis)
    graph.add_node("recommend_remediation", recommend_remediation)

    # Add edges
    graph.add_edge(START, "understand_incident")
    graph.add_edge("understand_incident", "collect_evidence")
    graph.add_edge("collect_evidence", "analyze_evidence")
    graph.add_edge("analyze_evidence", "form_hypotheses")
    graph.add_edge("form_hypotheses", "validate_hypothesis")
    graph.add_edge("validate_hypothesis", "recommend_remediation")
    graph.add_edge("recommend_remediation", END)

    return graph.compile()


# Singleton
investigation_graph = build_investigation_graph()
