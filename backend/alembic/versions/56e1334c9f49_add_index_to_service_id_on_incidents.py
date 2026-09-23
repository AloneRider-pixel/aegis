"""Add index to service_id on incidents

Revision ID: 56e1334c9f49
Revises: 20240514_add_incident_indexes
Create Date: 2026-09-23 13:16:07.687007

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56e1334c9f49'
down_revision: Union[str, None] = '20240514_add_incident_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_incidents_service_id', 'incidents', ['service_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_incidents_service_id', table_name='incidents')
