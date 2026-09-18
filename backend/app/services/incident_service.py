"""
Incident Service — business logic for incident lifecycle management.
"""
import uuid
from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Incident, IncidentEvent, IncidentStatus, Severity

# Valid state transitions
VALID_TRANSITIONS = {
    IncidentStatus.DETECTED: [IncidentStatus.ACKNOWLEDGED, IncidentStatus.INVESTIGATING],
    IncidentStatus.ACKNOWLEDGED: [IncidentStatus.INVESTIGATING],
    IncidentStatus.INVESTIGATING: [IncidentStatus.ROOT_CAUSE_IDENTIFIED, IncidentStatus.RESOLVED],
    IncidentStatus.ROOT_CAUSE_IDENTIFIED: [IncidentStatus.AWAITING_APPROVAL, IncidentStatus.REMEDIATING],
    IncidentStatus.AWAITING_APPROVAL: [IncidentStatus.REMEDIATING, IncidentStatus.INVESTIGATING],
    IncidentStatus.REMEDIATING: [IncidentStatus.VERIFYING, IncidentStatus.FAILED],
    IncidentStatus.VERIFYING: [IncidentStatus.RESOLVED, IncidentStatus.REMEDIATING],
    IncidentStatus.RESOLVED: [IncidentStatus.CLOSED],
    IncidentStatus.FAILED: [IncidentStatus.INVESTIGATING],
    IncidentStatus.CLOSED: [],
}


async def create_incident(
    db: AsyncSession,
    title: str,
    severity: str,
    service_id: str | None = None,
    description: str | None = None,
    symptoms: list[str] | None = None,
    source: str = "manual",
    environment: str = "production",
) -> Incident:
    """Create a new incident."""
    incident = Incident(
        id=uuid.uuid4(),
        title=title,
        description=description or "",
        severity=Severity(severity),
        status=IncidentStatus.DETECTED,
        service_id=uuid.UUID(service_id) if service_id else None,
        symptoms=symptoms or [],
        source=source,
        environment=environment,
        detected_at=datetime.utcnow(),
    )
    db.add(incident)

    # Create audit event
    event = IncidentEvent(
        id=uuid.uuid4(),
        incident_id=incident.id,
        event_type="status_change",
        new_status=IncidentStatus.DETECTED.value,
        actor="system",
        details={"title": title, "severity": severity},
    )
    db.add(event)
    await db.flush()
    await db.refresh(incident)
    return incident


async def transition_incident(
    db: AsyncSession,
    incident_id: str,
    new_status: str,
    actor: str = "system",
    details: dict | None = None,
) -> Incident:
    """Transition incident to a new status with validation."""
    result = await db.execute(select(Incident).where(Incident.id == uuid.UUID(incident_id)))
    incident = result.scalar_one_or_none()
    if not incident:
        raise ValueError("Incident not found")

    current = IncidentStatus(incident.status)
    target = IncidentStatus(new_status)

    if target not in VALID_TRANSITIONS.get(current, []):
        raise ValueError(f"Invalid transition: {current.value} -> {target.value}")

    old_status = incident.status
    incident.status = target

    # Update timeline fields
    now = datetime.utcnow()
    if target == IncidentStatus.ACKNOWLEDGED:
        incident.acknowledged_at = now
    elif target == IncidentStatus.INVESTIGATING:
        incident.investigation_started_at = now
    elif target == IncidentStatus.RESOLVED:
        incident.resolved_at = now

    # Audit event
    event = IncidentEvent(
        id=uuid.uuid4(),
        incident_id=incident.id,
        event_type="status_change",
        previous_status=current.value,
        new_status=target.value,
        actor=actor,
        details=details or {},
    )
    db.add(event)
    await db.flush()
    await db.refresh(incident)
    return incident


async def list_incidents(
    db: AsyncSession,
    status: str | None = None,
    severity: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple:
    """List incidents with optional filters."""
    query = select(Incident).order_by(desc(Incident.created_at))
    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)

    # ⚡ Bolt Optimization: Execute main query first and skip count query if total is obvious
    result = await db.execute(query.offset(offset).limit(limit))
    incidents = list(result.scalars().all())

    if offset == 0 and len(incidents) < limit:
        total = len(incidents)
    else:
        count_query = select(func.count()).select_from(Incident)
        if status:
            count_query = count_query.where(Incident.status == status)
        if severity:
            count_query = count_query.where(Incident.severity == severity)
        total = (await db.execute(count_query)).scalar() or 0

    return incidents, total


async def get_incident(db: AsyncSession, incident_id: str) -> Incident | None:
    """Get a single incident by ID."""
    result = await db.execute(select(Incident).where(Incident.id == uuid.UUID(incident_id)))
    return result.scalar_one_or_none()


async def get_incident_events(db: AsyncSession, incident_id: str) -> list[IncidentEvent]:
    """Get audit events for an incident."""
    result = await db.execute(
        select(IncidentEvent)
        .where(IncidentEvent.incident_id == uuid.UUID(incident_id))
        .order_by(IncidentEvent.created_at)
    )
    return list(result.scalars().all())


async def update_incident_investigation(
    db: AsyncSession,
    incident_id: str,
    root_cause: str | None = None,
    confidence: float | None = None,
    evidence: list[dict] | None = None,
    alternative_hypotheses: list[dict] | None = None,
    recommended_remediation: dict | None = None,
    investigation_trace: list[dict] | None = None,
):
    """Update incident with AI investigation results."""
    result = await db.execute(select(Incident).where(Incident.id == uuid.UUID(incident_id)))
    incident = result.scalar_one_or_none()
    if not incident:
        raise ValueError("Incident not found")

    if root_cause is not None:
        incident.probable_root_cause = root_cause
    if confidence is not None:
        incident.confidence = confidence
    if evidence is not None:
        incident.evidence = evidence
    if alternative_hypotheses is not None:
        incident.alternative_hypotheses = alternative_hypotheses
    if recommended_remediation is not None:
        incident.recommended_remediation = recommended_remediation
    if investigation_trace is not None:
        incident.investigation_trace = investigation_trace

    await db.flush()
    return incident


def search_similar_incidents(query: str, severity: str | None = None, top_k: int = 5) -> list[dict]:
    """
    Search previous incidents for similar patterns.
    Uses keyword matching against titles, root causes, and symptoms.
    """
    # In a real implementation, this would use pgvector for semantic search
    # For now, return empty results
    return []
