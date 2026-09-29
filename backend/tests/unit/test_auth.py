"""Tests for authentication utilities and HTTP bearer-header parsing."""

import pytest
from fastapi import HTTPException

from app.auth import create_token, decode_token
from app.main import get_current_user


class TestDecodeToken:
    def test_decode_token_success(self):
        token = create_token({"sub": "test_user"})
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "test_user"

    def test_decode_token_expired(self):
        token = create_token({"sub": "test_user"}, expires_minutes=-1)
        decoded = decode_token(token)
        assert decoded is None

    def test_decode_token_invalid_signature(self):
        token = create_token({"sub": "test_user"})
        parts = token.split(".")
        invalid_token = f"{parts[0]}.{parts[1]}.invalid_signature"

        decoded = decode_token(invalid_token)
        assert decoded is None

    def test_decode_token_malformed(self):
        invalid_token = "not.a.valid.jwt.token"
        decoded = decode_token(invalid_token)
        assert decoded is None


@pytest.mark.asyncio
async def test_bearer_header_without_token_returns_401():
    with pytest.raises(HTTPException) as exc:
        await get_current_user("Bearer")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_bearer_header_with_extra_spaces_is_parsed_safely():
    token = create_token({"sub": "test_user"})

    decoded = await get_current_user(f"Bearer    {token}")

    assert decoded["sub"] == "test_user"


@pytest.mark.asyncio
async def test_bearer_scheme_is_case_insensitive():
    token = create_token({"sub": "test_user"})

    decoded = await get_current_user(f"bearer {token}")

    assert decoded["sub"] == "test_user"


class FakeConnection:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, statement):
        return None


class FakeEngine:
    def connect(self):
        return FakeConnection()


class FakeRedis:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.closed = False

    async def ping(self):
        if self.should_fail:
            raise RuntimeError("redis unavailable")

    async def aclose(self):
        self.closed = True


@pytest.mark.asyncio
async def test_health_reports_healthy_when_dependencies_are_reachable(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr("app.main.engine", FakeEngine())
    monkeypatch.setattr("app.main.Redis.from_url", lambda _: fake_redis)

    response = await __import__("app.main", fromlist=["health"]).health()

    assert response.status == "healthy"
    assert response.database == "connected"
    assert response.redis == "connected"
    assert fake_redis.closed is True


@pytest.mark.asyncio
async def test_health_reports_degraded_when_redis_is_unavailable(monkeypatch):
    fake_redis = FakeRedis(should_fail=True)
    monkeypatch.setattr("app.main.engine", FakeEngine())
    monkeypatch.setattr("app.main.Redis.from_url", lambda _: fake_redis)

    response = await __import__("app.main", fromlist=["health"]).health()

    assert response.status == "degraded"
    assert response.database == "connected"
    assert response.redis == "unavailable"
    assert fake_redis.closed is True
