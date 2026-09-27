# Reviewer Guide

Recommended review path for a first technical pass:

1. Read `README.md` for the end-to-end incident workflow.
2. Inspect the LangGraph investigation state machine under `backend/app/ai/`.
3. Inspect the RAG retrieval boundary and pgvector data model.
4. Review the remediation approval and audit-trail paths.
5. Run the reproducible failure-simulation scenario before reviewing the evaluation API.

Engineering concerns intentionally documented in the repository include prompt-injection handling, authentication boundaries, idempotent state transitions, failure simulation, and evaluation integrity.