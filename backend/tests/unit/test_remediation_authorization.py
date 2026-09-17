import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from app.main import execute_remediation
from app.schemas import RemediationExecute


@pytest.mark.asyncio
async def test_viewer_cannot_execute_remediation():
    with pytest.raises(HTTPException) as exc:
        await execute_remediation(
            incident_id="00000000-0000-0000-0000-000000000000",
            req=RemediationExecute(
                incident_id="00000000-0000-0000-0000-000000000000",
                dry_run=True,
            ),
            user={"role": "viewer", "email": "viewer@example.com"},
            db=AsyncMock(),
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_engineer_cannot_execute_remediation():
    with pytest.raises(HTTPException) as exc:
        await execute_remediation(
            incident_id="00000000-0000-0000-0000-000000000000",
            req=RemediationExecute(
                incident_id="00000000-0000-0000-0000-000000000000",
                dry_run=True,
            ),
            user={"role": "engineer", "email": "engineer@example.com"},
            db=AsyncMock(),
        )

    assert exc.value.status_code == 403
