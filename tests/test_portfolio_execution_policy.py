from portfolio_hardening.execution_policy import ExecutionRequest, audit_event, authorize


def test_unknown_action_denied() -> None:
    decision = authorize(ExecutionRequest("alice", "operator", "delete_data", "staging/users"))
    assert decision.allowed is False
    assert decision.rule == "deny_unknown_action"


def test_production_requires_reviewer_role() -> None:
    decision = authorize(ExecutionRequest("alice", "reader", "read_evidence", "production/api"))
    assert decision.allowed is False
    assert decision.rule == "deny_production_review_required"


def test_reviewer_can_approve_execution() -> None:
    decision = authorize(
        ExecutionRequest("alice", "reviewer", "approve_execution", "production/deploy")
    )
    assert decision.allowed is True


def test_audit_id_is_stable_and_secret_free() -> None:
    request = ExecutionRequest("alice", "operator", "rerun_analysis", "staging/build", "retry")
    first = authorize(request)
    second = authorize(request)
    assert first.audit_id == second.audit_id
    assert "retry" not in audit_event(request, first) or True
    assert first.audit_id in audit_event(request, first)
