"""Database models for the Aegis platform."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, DateTime, Float, Integer, String, Text, Boolean, JSON, ForeignKey, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# ─── Enums ───

class IncidentStatus(str, PyEnum):
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    ROOT_CAUSE_IDENTIFIED = "root_cause_identified"
    AWAITING_APPROVAL = "awaiting_approval"
    REMEDIATING = "remediating"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    FAILED = "failed"
    CLOSED = "closed"


class Severity(str, PyEnum):
    SEV1 = "sev-1"
    SEV2 = "sev-2"
    SEV3 = "sev-3"
    SEV4 = "sev-4"


class UserRole(str, PyEnum):
    VIEWER = "viewer"
    ENGINEER = "engineer"
    INCIDENT_MANAGER = "incident_manager"
    ADMIN = "admin"


# ─── User Model ───

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ENGINEER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─── Service Model ───

class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    team = Column(String(255))
    environment = Column(String(50), default="production")
    health_status = Column(String(50), default="healthy")
    last_check_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─── Incident Model ───

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(Enum(Severity), nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.DETECTED)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    environment = Column(String(50), default="production")
    source = Column(String(100))  # "auto_detected", "manual", "simulator"

    # Timeline
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    investigation_started_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Symptoms
    symptoms = Column(JSON, default=list)

    # AI Investigation Results
    probable_root_cause = Column(Text)
    confidence = Column(Float)
    evidence = Column(JSON, default=list)
    alternative_hypotheses = Column(JSON, default=list)
    investigation_trace = Column(JSON, default=list)

    # Remediation
    recommended_remediation = Column(JSON)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    remediation_result = Column(JSON)
    resolution_summary = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan")
    service = relationship("Service")


# ─── Incident Event (Audit Trail) ───

class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    event_type = Column(String(100), nullable=False)  # "status_change", "ai_step", "tool_call", "remediation"
    previous_status = Column(String(50))
    new_status = Column(String(50))
    actor = Column(String(255))  # "system", "user:email", "ai-agent"
    details = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="events")


# ─── Knowledge Document ───

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(50))  # "runbook", "postmortem", "architecture", "guide"
    service = Column(String(255))
    environment = Column(String(50))
    version = Column(String(50))
    source = Column(String(255))
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─── Audit Log ───

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    details = Column(JSON, default=dict)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─── Evaluation ───

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_name = Column(String(100), nullable=False)
    num_scenarios = Column(Integer, nullable=False)
    root_cause_accuracy = Column(Float)
    evidence_grounding = Column(Float)
    hallucination_rate = Column(Float)
    avg_latency_seconds = Column(Float)
    total_cost_usd = Column(Float)
    total_tokens = Column(Integer)
    results = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
