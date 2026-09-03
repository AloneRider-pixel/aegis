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
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str


# ─── Incident ───

class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "sev-3"
    service_id: Optional[str] = None
    environment: str = "production"
    source: str = "manual"
    symptoms: List[str] = []

class IncidentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    severity: str
    status: str
    service_id: Optional[str]
    environment: str
    source: str
    detected_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    investigation_started_at: Optional[datetime]
    resolved_at: Optional[datetime]
    assigned_to: Optional[str]
    symptoms: List[str]
    probable_root_cause: Optional[str]
    confidence: Optional[float]
    evidence: List[Dict[str, Any]]
    alternative_hypotheses: List[Dict[str, Any]]
    recommended_remediation: Optional[Dict[str, Any]]
    approved_by: Optional[str]
    resolution_summary: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class IncidentListResponse(BaseModel):
    incidents: List[IncidentResponse]
    total: int

class IncidentEventResponse(BaseModel):
    id: str
    incident_id: str
    event_type: str
    previous_status: Optional[str]
    new_status: Optional[str]
    actor: str
    details: Dict[str, Any]
    created_at: datetime


# ─── Investigation ───

class InvestigationStart(BaseModel):
    incident_id: str

class InvestigationResponse(BaseModel):
    incident_id: str
    status: str
    root_cause: Optional[str]
    confidence: Optional[float]
    evidence: List[Dict[str, Any]]
    investigation_trace: List[Dict[str, Any]]
    recommended_remediation: Optional[Dict[str, Any]]


# ─── Remediation ───

class RemediationApproval(BaseModel):
    incident_id: str
    approved: bool = True
    notes: Optional[str] = None

class RemediationExecute(BaseModel):
    incident_id: str
    dry_run: bool = True  # Default to dry run for safety


# ─── Knowledge ───

class DocumentCreate(BaseModel):
    title: str
    content: str
    document_type: str = "runbook"
    service: Optional[str] = None
    environment: Optional[str] = None

class KnowledgeSearchRequest(BaseModel):
    query: str
    service: Optional[str] = None
    document_type: Optional[str] = None
    top_k: int = 5

class KnowledgeSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
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
    results: List[Dict[str, Any]]


# ─── Service ───

class ServiceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    team: Optional[str]
    environment: str
    health_status: str
    last_check_at: Optional[datetime]


# ─── Health ───

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    llm_provider: str
