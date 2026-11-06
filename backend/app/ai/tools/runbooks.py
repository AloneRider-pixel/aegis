"""
Runbooks Tool — searches the RAG knowledge base for relevant runbooks.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def search_runbook(
    query: str,
    service: str | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    """
    Search the knowledge base for relevant runbooks.
    Uses pgvector for semantic search with metadata filtering.
    """
    from app.services.knowledge_service import search_knowledge

    results = search_knowledge(
        query=query,
        service=service,
        document_type="runbook",
        top_k=top_k,
    )

    return {
        "query": query,
        "service": service,
        "results": results,
        "total_found": len(results),
        "source": "rag_knowledge_base",
    }


def search_previous_incidents(
    query: str,
    severity: str | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    """
    Search previous incidents for similar patterns.
    Helps the agent learn from past incidents.
    """
    try:
        from app.services.incident_service import search_similar_incidents

        results = search_similar_incidents(query=query, severity=severity, top_k=top_k)
        note = "Historical evidence — distinguish from current incident evidence"
    except Exception as exc:  # noqa: BLE001 - history must never crash an
        # investigation; its import chain pulls in the database stack, which
        # is absent in offline/tool-only environments. The reason is logged.
        logger.warning("incident history unavailable (%s: %s); continuing "
                       "from current evidence only", type(exc).__name__, exc)
        results = []
        note = "Incident history unavailable; investigation continues from current evidence only"

    return {
        "query": query,
        "results": results,
        "total_found": len(results),
        "source": "incident_history",
        "note": note,
    }
