"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# ─── Auth ───

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str


# ─── Incident ───

class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    severity: str = "sev-3"
    service_id: str | None = None
    environment: str = "production"
    source: str = "manual"
    symptoms: list[str] = []

class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str | None
    severity: str
    status: str
    service_id: str | None
    environment: str
    source: str
    detected_at: datetime | None
    acknowledged_at: datetime | None
    investigation_started_at: datetime | None
    resolved_at: datetime | None
    assigned_to: str | None
    symptoms: list[str]
    probable_root_cause: str | None
    confidence: float | None
    evidence: list[dict[str, Any]]
    alternative_hypotheses: list[dict[str, Any]]
    recommended_remediation: dict[str, Any] | None
    approved_by: str | None
    resolution_summary: str | None
    created_at: datetime | None
    updated_at: datetime | None

class IncidentListResponse(BaseModel):
    incidents: list[IncidentResponse]
    total: int

class IncidentEventResponse(BaseModel):
    id: str
    incident_id: str
    event_type: str
    previous_status: str | None
    new_status: str | None
    actor: str
    details: dict[str, Any]
    created_at: datetime


# ─── Investigation ───

class InvestigationStart(BaseModel):
    incident_id: str

class InvestigationResponse(BaseModel):
    incident_id: str
    status: str
    root_cause: str | None
    confidence: float | None
    evidence: list[dict[str, Any]]
    investigation_trace: list[dict[str, Any]]
    recommended_remediation: dict[str, Any] | None


# ─── Remediation ───

class RemediationApproval(BaseModel):
    incident_id: str
    approved: bool = True
    notes: str | None = None

class RemediationExecute(BaseModel):
    incident_id: str
    dry_run: bool = True  # Default to dry run for safety


# ─── Knowledge ───

class DocumentCreate(BaseModel):
    title: str
    content: str
    document_type: str = "runbook"
    service: str | None = None
    environment: str | None = None

class KnowledgeSearchRequest(BaseModel):
    query: str
    service: str | None = None
    document_type: str | None = None
    top_k: int = 5

class KnowledgeSearchResponse(BaseModel):
    results: list[dict[str, Any]]
    total: int


# ─── Simulator ───

class SimulatorTrigger(BaseModel):
    scenario: str
    environment: str = "production"

class SimulatorScenario(BaseModel):
    id: str
    name: str
    description: str
    severity: str
    category: str


# ─── Evaluation ───

class EvaluationRequest(BaseModel):
    dataset: str = "default"
    num_scenarios: int = 10

class EvaluationResponse(BaseModel):
    run_id: str
    dataset: str
    num_scenarios: int
    root_cause_accuracy: float
    evidence_grounding: float
    hallucination_rate: float
    avg_latency_seconds: float
    total_cost_usd: float
    results: list[dict[str, Any]]


# ─── Service ───

class ServiceResponse(BaseModel):
    id: str
    name: str
    description: str | None
    team: str | None
    environment: str
    health_status: str
    last_check_at: datetime | None


# ─── Health ───

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    llm_provider: str
