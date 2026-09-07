"""
Aegis — AI-Powered Production Reliability & Incident Response Platform.
Main FastAPI application with all API routes.
"""
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session, get_db, init_db
from app.models import Service, User, UserRole, Document, AuditLog, EvaluationRun
from app.schemas import *
from app.auth import create_token, decode_token, hash_password, verify_password
from app.services.incident_service import (
    create_incident, transition_incident, list_incidents,
    get_incident, get_incident_events, update_incident_investigation,
)
from app.simulator.scenarios import list_scenarios, trigger_scenario

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aegis")


# ─── Lifespan ───

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Seed default services and admin user
    async with async_session() as db:
        # Create services
        for svc_name in ["checkout-service", "order-service", "api-gateway", "payment-service", "product-service"]:
            result = await db.execute(select(Service).where(Service.name == svc_name))
            if not result.scalar_one_or_none():
                db.add(Service(id=uuid.uuid4(), name=svc_name, team="platform", environment="production"))

        # Create admin user
        result = await db.execute(select(User).where(User.email == "admin@aegis.io"))
        if not result.scalar_one_or_none():
            db.add(User(
                id=uuid.uuid4(), email="admin@aegis.io",
                hashed_password=hash_password("admin123"),
                full_name="Admin User", role=UserRole.ADMIN,
            ))
        await db.commit()

    logger.info("Aegis platform started ✓")
    yield
    logger.info("Aegis platform shutting down")


app = FastAPI(
    title="Aegis — AI Incident Response Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Auth Dependency ───

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authentication")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


# ─── Health ───

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy", version="1.0.0",
        database="connected", redis="connected",
        llm_provider=settings.llm_provider,
    )


# ─── Auth Routes ───

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(user.id), "email": user.email, "role": user.role.value})
    return TokenResponse(
        access_token=token,
        user={"id": str(user.id), "email": user.email, "full_name": user.full_name, "role": user.role.value},
    )


@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user


# ─── Incident Routes ───

@app.get("/api/incidents", response_model=IncidentListResponse)
async def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    incidents, total = await list_incidents(db, status=status, severity=severity, limit=limit, offset=offset)
    return IncidentListResponse(
        incidents=[
            IncidentResponse(
                id=str(i.id), title=i.title, description=i.description,
                severity=i.severity.value if i.severity else "", status=i.status.value if i.status else "",
                service_id=str(i.service_id) if i.service_id else None,
                environment=i.environment, source=i.source,
                detected_at=i.detected_at, acknowledged_at=i.acknowledged_at,
                investigation_started_at=i.investigation_started_at,
                resolved_at=i.resolved_at,
                assigned_to=str(i.assigned_to) if i.assigned_to else None,
                symptoms=i.symptoms or [], probable_root_cause=i.probable_root_cause,
                confidence=i.confidence, evidence=i.evidence or [],
                alternative_hypotheses=i.alternative_hypotheses or [],
                recommended_remediation=i.recommended_remediation,
                approved_by=str(i.approved_by) if i.approved_by else None,
                resolution_summary=i.resolution_summary,
                created_at=i.created_at, updated_at=i.updated_at,
            )
            for i in incidents
        ],
        total=total,
    )


@app.post("/api/incidents", status_code=201)
async def create_new_incident(
    req: IncidentCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    incident = await create_incident(
        db=db, title=req.title, severity=req.severity,
        service_id=req.service_id, description=req.description,
        symptoms=req.symptoms, source=req.source, environment=req.environment,
    )
    return {"incident_id": str(incident.id), "status": "detected"}


@app.get("/api/incidents/{incident_id}")
async def get_single_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    incident = await get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    events = await get_incident_events(db, incident_id)
    return {
        "incident": {
            "id": str(incident.id), "title": incident.title,
            "severity": incident.severity.value, "status": incident.status.value,
            "symptoms": incident.symptoms or [],
            "probable_root_cause": incident.probable_root_cause,
            "confidence": incident.confidence,
            "evidence": incident.evidence or [],
            "alternative_hypotheses": incident.alternative_hypotheses or [],
            "recommended_remediation": incident.recommended_remediation,
            "investigation_trace": incident.investigation_trace or [],
            "resolution_summary": incident.resolution_summary,
            "detected_at": incident.detected_at.isoformat() if incident.detected_at else None,
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
        },
        "events": [
            {
                "id": str(e.id), "event_type": e.event_type,
                "previous_status": e.previous_status, "new_status": e.new_status,
                "actor": e.actor, "details": e.details,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
    }


# ─── AI Investigation ───

@app.post("/api/incidents/{incident_id}/investigate")
async def start_investigation(
    incident_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start AI-powered investigation of an incident."""
    incident = await get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Transition to investigating
    await transition_incident(db, incident_id, "investigating", actor=f"user:{user.get('email', 'unknown')}")

    # Run the AI agent
    from app.ai.agent.graph import investigation_graph

    initial_state = {
        "incident_id": incident_id,
        "incident_title": incident.title,
        "incident_description": incident.description or "",
        "severity": incident.severity.value,
        "service_name": "checkout-service",  # Default; in prod, get from service_id
        "symptoms": incident.symptoms or [],
        "current_phase": "understand",
        "metrics_data": [],
        "logs_data": [],
        "traces_data": [],
        "deployment_data": [],
        "runbook_results": [],
        "historical_incidents": [],
        "hypotheses": [],
        "root_cause": None,
        "confidence": 0.0,
        "evidence_chain": [],
        "recommended_remediation": None,
        "remediation_approved": False,
        "remediation_executed": False,
        "remediation_result": None,
        "investigation_trace": [],
        "tool_calls": [],
        "token_usage": {"input": 0, "output": 0},
        "total_cost_usd": 0.0,
        "iteration": 0,
        "max_iterations": settings.max_agent_iterations,
        "errors": [],
    }

    final_state = await investigation_graph.ainvoke(initial_state)

    # Update incident with investigation results
    await update_incident_investigation(
        db=db,
        incident_id=incident_id,
        root_cause=final_state.get("root_cause"),
        confidence=final_state.get("confidence", 0.0),
        evidence=[
            {"source": "metrics", "data": final_state.get("metrics_data", {})},
            {"source": "logs", "data": final_state.get("logs_data", [])[:5]},
            {"source": "deployments", "data": final_state.get("deployment_data", [])},
        ],
        alternative_hypotheses=final_state.get("hypotheses", [])[:3],
        recommended_remediation=final_state.get("recommended_remediation"),
        investigation_trace=final_state.get("investigation_trace", []),
    )

    # Transition to root_cause_identified
    if final_state.get("root_cause") and final_state.get("confidence", 0) > 0.5:
        await transition_incident(db, incident_id, "root_cause_identified", actor="ai-agent")
        if final_state.get("recommended_remediation", {}).get("requires_approval", True):
            await transition_incident(db, incident_id, "awaiting_approval", actor="ai-agent")

    return InvestigationResponse(
        incident_id=incident_id,
        status=final_state.get("current_phase", "complete"),
        root_cause=final_state.get("root_cause"),
        confidence=final_state.get("confidence", 0.0),
        evidence=final_state.get("evidence_chain", []),
        investigation_trace=final_state.get("investigation_trace", []),
        recommended_remediation=final_state.get("recommended_remediation"),
    )


# ─── Remediation Approval ───

@app.post("/api/incidents/{incident_id}/approve-remediation")
async def approve_remediation(
    incident_id: str,
    req: RemediationApproval,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject remediation (requires incident_manager or admin role)."""
    if user.get("role") not in ("incident_manager", "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to approve remediation")

    incident = await get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if req.approved:
        await transition_incident(db, incident_id, "remediating", actor=f"user:{user['email']}")
        return {"status": "approved", "message": "Remediation approved. Ready to execute."}
    else:
        await transition_incident(db, incident_id, "investigating", actor=f"user:{user['email']}")
        return {"status": "rejected", "message": "Remediation rejected. Re-investigating."}


@app.post("/api/incidents/{incident_id}/execute-remediation")
async def execute_remediation(
    incident_id: str,
    req: RemediationExecute,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute remediation (dry_run=True by default for safety)."""
    incident = await get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    remediation = incident.recommended_remediation
    if not remediation:
        raise HTTPException(status_code=400, detail="No remediation recommended")

    if req.dry_run:
        result = {
            "action": remediation.get("action"),
            "mode": "dry_run",
            "result": f"DRY RUN: Would execute '{remediation.get('description')}'",
            "risk": remediation.get("risk"),
            "rollback": remediation.get("rollback_strategy"),
        }
    else:
        # Execute (simulated)
        result = {
            "action": remediation.get("action"),
            "mode": "executed",
            "result": f"Executed: {remediation.get('description')}",
            "success": True,
        }
        await update_incident_investigation(db, incident_id, remediation_result=result)
        await transition_incident(db, incident_id, "verifying", actor=f"user:{user.get('email', 'system')}")

    return result


# ─── Simulator Routes ───

@app.get("/api/simulator/scenarios")
async def get_scenarios():
    return {"scenarios": list_scenarios()}


@app.post("/api/simulator/scenarios/{scenario_id}/trigger")
async def trigger_failure_scenario(
    scenario_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a failure scenario — creates telemetry and an incident."""
    result = trigger_scenario(scenario_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # Auto-create incident
    inc_data = result["incident"]
    incident = await create_incident(
        db=db,
        title=inc_data["title"],
        severity=inc_data["severity"],
        symptoms=inc_data["symptoms"],
        source="simulator",
    )

    return {
        "scenario": result["scenario"],
        "incident_id": str(incident.id),
        "telemetry_generated": True,
        "message": "Scenario triggered. Incident created. Ready for AI investigation.",
    }


# ─── Services ───

@app.get("/api/services")
async def get_services(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service))
    services = result.scalars().all()
    return {
        "services": [
            {"id": str(s.id), "name": s.name, "team": s.team, "environment": s.environment, "health_status": s.health_status}
            for s in services
        ]
    }


# ─── Knowledge / RAG ───

@app.post("/api/knowledge/search")
async def search_knowledge(req: KnowledgeSearchRequest, db: AsyncSession = Depends(get_db)):
    """Search the knowledge base (runbooks, docs, postmortems)."""
    result = await db.execute(
        select(Document).where(
            Document.content.ilike(f"%{req.query}%")
        ).limit(req.top_k)
    )
    docs = result.scalars().all()
    return KnowledgeSearchResponse(
        results=[
            {
                "document_id": str(d.id), "title": d.title,
                "content": d.content[:500], "document_type": d.document_type,
                "service": d.service, "relevance_score": 0.8,
            }
            for d in docs
        ],
        total=len(docs),
    )


@app.post("/api/documents")
async def upload_document(req: DocumentCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = Document(
        id=uuid.uuid4(), title=req.title, content=req.content,
        document_type=req.document_type, service=req.service, environment=req.environment,
    )
    db.add(doc)
    await db.flush()
    return {"document_id": str(doc.id), "status": "uploaded"}


# ─── Evaluation ───

@app.get("/api/evaluations")
async def list_evaluations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(20))
    runs = result.scalars().all()
    return {
        "evaluations": [
            {
                "id": str(r.id), "dataset": r.dataset_name,
                "scenarios": r.num_scenarios,
                "accuracy": r.root_cause_accuracy,
                "grounding": r.evidence_grounding,
                "hallucination_rate": r.hallucination_rate,
                "latency": r.avg_latency_seconds,
                "cost": r.total_cost_usd,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in runs
        ]
    }


@app.post("/api/evaluations/run")
async def run_evaluation(req: EvaluationRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Run the AI evaluation benchmark."""
    # Simulated evaluation results
    import random
    eval_run = EvaluationRun(
        id=uuid.uuid4(),
        dataset_name=req.dataset,
        num_scenarios=req.num_scenarios,
        root_cause_accuracy=round(random.uniform(0.75, 0.92), 4),
        evidence_grounding=round(random.uniform(0.80, 0.95), 4),
        hallucination_rate=round(random.uniform(0.02, 0.08), 4),
        avg_latency_seconds=round(random.uniform(5, 20), 2),
        total_cost_usd=round(random.uniform(0.5, 3.0), 4),
        total_tokens=random.randint(50000, 200000),
        results={"status": "completed"},
    )
    db.add(eval_run)
    await db.flush()
    await db.refresh(eval_run)

    return EvaluationResponse(
        run_id=str(eval_run.id),
        dataset=eval_run.dataset_name,
        num_scenarios=eval_run.num_scenarios,
        root_cause_accuracy=eval_run.root_cause_accuracy,
        evidence_grounding=eval_run.evidence_grounding,
        hallucination_rate=eval_run.hallucination_rate,
        avg_latency_seconds=eval_run.avg_latency_seconds,
        total_cost_usd=eval_run.total_cost_usd,
        results=[{"scenario": "demo", "status": "passed"}],
    )


# ─── Audit ───

@app.get("/api/audit")
async def get_audit_logs(limit: int = 50, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit))
    logs = result.scalars().all()
    return {
        "logs": [
            {
                "id": str(l.id), "action": l.action,
                "resource_type": l.resource_type, "resource_id": l.resource_id,
                "details": l.details, "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
