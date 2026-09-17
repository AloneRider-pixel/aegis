# Engineering Notes

## Engineering focus
Aegis is a production-reliability reference system centered on evidence-backed incident investigation, explicit agent/tool boundaries, human-approved remediation, and auditability.

## Key design decisions
- **LangGraph state machine:** keeps investigation phases explicit and inspectable.
- **Tool-mediated evidence:** metrics, logs, traces, deployments, runbooks, and incident history are treated as evidence sources rather than free-form model context.
- **RAG with pgvector:** operational knowledge is retrieved from runbooks and postmortems.
- **Human-in-the-loop remediation:** impactful actions require approval.
- **Evaluation-first AI:** root-cause quality, grounding, hallucination rate, latency, and cost are measurable concerns.

## Verification checklist
- Run `docker compose up -d`.
- Apply migrations and seed the knowledge base.
- Run `pytest tests/` and the evaluation script.
- Trigger the documented database-connection-exhaustion scenario.

## Portfolio note
Claims in the project README should be updated only when reproduced by the repository's current evaluation/test harness.
