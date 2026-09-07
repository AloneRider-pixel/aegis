import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth import create_token
from app.models import UserRole

@pytest.mark.asyncio
async def test_get_audit_logs_unauthenticated():
    # Override database dependency for unauthenticated to avoid db calls
    from app.main import get_db
    app.dependency_overrides[get_db] = lambda: None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/audit")
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing authentication"}
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_audit_logs_authenticated(mocker):
    # Mock db response
    from unittest.mock import AsyncMock, MagicMock
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    from app.main import get_db
    app.dependency_overrides[get_db] = lambda: mock_db

    token = create_token({"sub": "test-user-id", "email": "test@example.com", "role": UserRole.ENGINEER.value})
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/audit", headers=headers)
    assert response.status_code == 200
    assert "logs" in response.json()
    app.dependency_overrides.clear()
