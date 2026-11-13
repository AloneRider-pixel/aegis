"""Tests for the knowledge service (ILIKE baseline contract)."""
import os
import uuid

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key")
os.environ.setdefault("DEFAULT_ADMIN_PASSWORD", "test-admin-password")

import pytest
from sqlalchemy import create_engine

from app.database import Base
from app.models import Document
from app.services.knowledge_service import search_knowledge


@pytest.fixture()
def db_url(tmp_path):
    url = f"sqlite:///{tmp_path}/knowledge.db"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    from sqlalchemy.orm import Session
    with Session(engine) as s:
        s.add_all([
            Document(id=uuid.uuid4(), title="DB pool runbook",
                     content="When the connection pool is exhausted, raise the cap and recycle idle clients.",
                     document_type="runbook", service="checkout"),
            Document(id=uuid.uuid4(), title="Deploy rollback runbook",
                     content="If a release correlates with a 5xx spike, roll back the deployment first.",
                     document_type="runbook", service="checkout"),
            Document(id=uuid.uuid4(), title="Old incident writeup",
                     content="Postmortem: the connection pool saturated after a traffic surge.",
                     document_type="postmortem", service="billing"),
        ])
        s.commit()
    engine.dispose()
    return url


def test_substring_match_returns_documents(db_url):
    results = search_knowledge("connection pool", db_url=db_url)
    assert len(results) == 2
    assert {r["title"] for r in results} == {"DB pool runbook", "Old incident writeup"}
    assert all(set(r) == {"document_id", "title", "content", "document_type",
                          "service", "relevance_score"} for r in results)


def test_metadata_filters(db_url):
    runbooks = search_knowledge("connection pool", document_type="runbook", db_url=db_url)
    assert [r["title"] for r in runbooks] == ["DB pool runbook"]
    billing = search_knowledge("connection pool", service="billing", db_url=db_url)
    assert [r["title"] for r in billing] == ["Old incident writeup"]


def test_top_k_limits_results(db_url):
    assert len(search_knowledge("connection pool", top_k=1, db_url=db_url)) == 1


def test_no_match_returns_empty(db_url):
    assert search_knowledge("kubernetes", db_url=db_url) == []


def test_blank_query_returns_empty(db_url):
    assert search_knowledge("   ", db_url=db_url) == []


def test_unreachable_database_degrades_to_empty_not_crash():
    # Port 1 refuses immediately: the agent investigates from telemetry alone.
    assert search_knowledge("anything", db_url="postgresql://u:p@127.0.0.1:1/none") == []


class TestPreviousIncidentsTool:
    def test_returns_empty_history_with_evidence_note(self):
        from app.ai.tools.runbooks import search_previous_incidents
        out = search_previous_incidents("5xx spike")
        assert out["results"] == [] and out["total_found"] == 0
        assert out["source"] == "incident_history" and out["note"]

    def test_search_runbook_degrades_without_database(self):
        # No Postgres in the unit-test environment: the tool must return an
        # empty result set with its source label, not raise.
        from app.ai.tools.runbooks import search_runbook
        out = search_runbook("connection pool", service="checkout")
        assert out["results"] == [] and out["source"] == "rag_knowledge_base"


def test_cached_engine_is_reused_and_not_disposed_per_search(db_url, monkeypatch):
    import sqlalchemy

    from app.services import knowledge_service
    knowledge_service._get_engine.cache_clear()
    created = []
    original = sqlalchemy.create_engine

    def track(url):
        engine = original(url)
        created.append(engine)
        return engine

    monkeypatch.setattr(sqlalchemy, 'create_engine', track)
    try:
        first = search_knowledge('connection pool', db_url=db_url)
        assert first
        assert len(created) == 1
        original_dispose = created[0].dispose
        disposed = []
        monkeypatch.setattr(created[0], 'dispose', lambda: disposed.append(True))
        assert search_knowledge('connection pool', db_url=db_url) == first
        assert search_knowledge('connection pool', service='billing', db_url=db_url)
        assert len(created) == 1
        assert not disposed
        assert knowledge_service._get_engine(db_url) is created[0]
        assert knowledge_service._get_engine.cache_info().maxsize == 4
    finally:
        for engine in created:
            original_dispose()
        knowledge_service._get_engine.cache_clear()


def test_cached_engines_keep_database_urls_separate(tmp_path):
    from app.services.knowledge_service import _get_engine
    one = _get_engine(f'sqlite:///{tmp_path}/one.db')
    two = _get_engine(f'sqlite:///{tmp_path}/two.db')
    try:
        assert one is not two
        assert _get_engine(f'sqlite:///{tmp_path}/one.db') is one
    finally:
        one.dispose()
        two.dispose()
        _get_engine.cache_clear()
