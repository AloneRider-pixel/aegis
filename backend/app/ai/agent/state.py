"""
Agent State — defines the data flowing through the investigation graph.
"""
from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict):
    """State that flows through the investigation LangGraph."""

    # Incident context
    incident_id: str
    incident_title: str
    incident_description: str
    severity: str
    service_name: str
    symptoms: List[str]

    # Investigation phases
    current_phase: str  # understand, collect_evidence, analyze, hypothesize, recommend

    # Evidence collected
    metrics_data: List[Dict[str, Any]]
    logs_data: List[Dict[str, Any]]
    traces_data: List[Dict[str, Any]]
    deployment_data: List[Dict[str, Any]]
    runbook_results: List[Dict[str, Any]]
    historical_incidents: List[Dict[str, Any]]

    # Analysis
    hypotheses: List[Dict[str, Any]]
    root_cause: Optional[str]
    confidence: float
    evidence_chain: List[Dict[str, Any]]

    # Remediation
    recommended_remediation: Optional[Dict[str, Any]]
    remediation_approved: bool
    remediation_executed: bool
    remediation_result: Optional[Dict[str, Any]]

    # Trace
    investigation_trace: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    token_usage: Dict[str, int]
    total_cost_usd: float

    # Safety
    iteration: int
    max_iterations: int
    errors: List[str]
