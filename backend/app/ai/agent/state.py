"""
Agent State — defines the data flowing through the investigation graph.
"""
from typing import Any, TypedDict


class AgentState(TypedDict):
    """State that flows through the investigation LangGraph."""

    # Incident context
    incident_id: str
    incident_title: str
    incident_description: str
    severity: str
    service_name: str
    symptoms: list[str]

    # Investigation phases
    current_phase: str  # understand, collect_evidence, analyze, hypothesize, recommend

    # Evidence collected
    metrics_data: list[dict[str, Any]]
    logs_data: list[dict[str, Any]]
    traces_data: list[dict[str, Any]]
    deployment_data: list[dict[str, Any]]
    runbook_results: list[dict[str, Any]]
    historical_incidents: list[dict[str, Any]]

    # Analysis
    hypotheses: list[dict[str, Any]]
    root_cause: str | None
    confidence: float
    evidence_chain: list[dict[str, Any]]

    # Remediation
    recommended_remediation: dict[str, Any] | None
    remediation_approved: bool
    remediation_executed: bool
    remediation_result: dict[str, Any] | None

    # Trace
    investigation_trace: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]
    token_usage: dict[str, int]
    total_cost_usd: float

    # Safety
    iteration: int
    max_iterations: int
    errors: list[str]
