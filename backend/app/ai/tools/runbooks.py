"""
Runbooks Tool — searches the RAG knowledge base for relevant runbooks.
"""
from typing import Any, Dict


def search_runbook(
    query: str,
    service: str = None,
    top_k: int = 3,
) -> Dict[str, Any]:
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
    severity: str = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Search previous incidents for similar patterns.
    Helps the agent learn from past incidents.
    """
    from app.services.incident_service import search_similar_incidents

    results = search_similar_incidents(query=query, severity=severity, top_k=top_k)

    return {
        "query": query,
        "results": results,
        "total_found": len(results),
        "source": "incident_history",
        "note": "Historical evidence — distinguish from current incident evidence",
    }
