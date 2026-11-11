"""
Knowledge Service - the knowledge-base query path the agent's runbook tool
expects (app.ai.tools.runbooks imports search_knowledge from here; its
absence crashed every investigation at the analyze_evidence node).

The contract implemented here is the one the repo already documents:

- app/main.py's POST /api/knowledge/search defines the current design: a
  SQL ILIKE substring baseline over the documents table with optional
  metadata filters (service, document_type) and an uncalibrated constant
  relevance score. pgvector semantic retrieval remains intended
  architecture, not a working path in this revision.
- The agent tools are synchronous, so this module queries through the sync
  database URL (settings.database_url; psycopg2 is a declared dependency)
  with a short-lived engine per call.

When no database is configured or reachable (offline runs, the eval
harness), the search logs the reason and returns an empty list: the agent
then investigates from telemetry alone instead of crashing. An empty
knowledge base is a truthful answer; a fabricated runbook would not be.
"""
import logging
import functools
from typing import Any

logger = logging.getLogger(__name__)

# Same uncalibrated constant the HTTP endpoint returns today (see README's
# honesty note on the ILIKE baseline). Not a semantic relevance score.
_RESULT_SCORE = 0.8
_CONTENT_PREVIEW = 500  # same truncation as the HTTP endpoint


@functools.lru_cache(maxsize=4)
def get_engine(url):
    from sqlalchemy import create_engine
    return create_engine(url)


def search_knowledge(
    query: str,
    service: "str | None" = None,
    document_type: "str | None" = None,
    top_k: int = 5,
    db_url: "str | None" = None,  # injectable for tests; defaults to settings
) -> "list[dict[str, Any]]":
    """Substring search over the documents table (ILIKE baseline).

    Returns one dict per matching document: document_id, title, content
    (first 500 chars), document_type, service, relevance_score.
    """
    if not query or not query.strip():
        return []
    try:
        if db_url is None:
            from app.config import settings
            db_url = settings.database_url
        from sqlalchemy import select
        from sqlalchemy.orm import Session

        from app.models import Document

        engine = get_engine(db_url)
        with Session(engine) as session:
            stmt = select(Document).where(
                Document.content.ilike(f"%{query}%"))
            if service:
                stmt = stmt.where(Document.service == service)
            if document_type:
                stmt = stmt.where(Document.document_type == document_type)
            stmt = stmt.limit(top_k)
            docs = session.scalars(stmt).all()
            return [{
                "document_id": str(d.id),
                "title": d.title,
                "content": d.content[:_CONTENT_PREVIEW],
                "document_type": d.document_type,
                "service": d.service,
                "relevance_score": _RESULT_SCORE,
            } for d in docs]
    except Exception as exc:  # noqa: BLE001 - a missing/unreachable knowledge
        # base must degrade the investigation, never crash it; the reason is
        # logged so the degradation is visible in the audit trail.
        logger.warning("knowledge search unavailable (%s: %s); returning no results",
                       type(exc).__name__, exc)
        return []
