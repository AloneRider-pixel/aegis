from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


ALLOWED_ACTIONS = frozenset({"read_evidence", "rerun_analysis", "approve_execution"})
REVIEWER_ROLES = frozenset({"reviewer", "operator"})


@dataclass(frozen=True)
class ExecutionRequest:
    actor: str
    role: str
    action: str
    resource: str
    reason: str = ""


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    rule: str
    audit_id: str


def _audit_id(request: ExecutionRequest) -> str:
    material = "|".join(
        (request.actor, request.role, request.action, request.resource, request.reason)
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def authorize(request: ExecutionRequest) -> PolicyDecision:
    audit_id = _audit_id(request)
    if request.action not in ALLOWED_ACTIONS:
        return PolicyDecision(False, "deny_unknown_action", audit_id)
    if not request.actor.strip() or not request.resource.strip():
        return PolicyDecision(False, "deny_invalid_identity", audit_id)
    if request.action == "approve_execution" and request.role not in REVIEWER_ROLES:
        return PolicyDecision(False, "deny_reviewer_role_required", audit_id)
    if request.resource.startswith("production/") and request.role not in REVIEWER_ROLES:
        return PolicyDecision(False, "deny_production_review_required", audit_id)
    return PolicyDecision(True, "allow_policy", audit_id)


def audit_event(request: ExecutionRequest, decision: PolicyDecision) -> str:
    event = {
        "audit_id": decision.audit_id,
        "actor": request.actor,
        "action": request.action,
        "resource": request.resource,
        "allowed": decision.allowed,
        "rule": decision.rule,
    }
    return json.dumps(event, sort_keys=True, separators=(",", ":"))
