import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from app.main import approve_remediation
from app.schemas import RemediationApproval


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["viewer", "engineer"])
async def test_non_manager_cannot_approve_remediation(role):
    with pytest.raises(HTTPException) as exc:
        await approve_remediation(
            incident_id="00000000-0000-0000-0000-000000000000",
            req=RemediationApproval(
                incident_id="00000000-0000-0000-0000-000000000000",
                approved=True,
            ),
            user={"role": role, "email": f"{role}@example.com"},
            db=AsyncMock(),
        )

    assert exc.value.status_code == 403
