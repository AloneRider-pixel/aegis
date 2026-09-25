"""Add index to created_at

Revision ID: dd662b83a8c3
Revises: 20240514_add_incident_indexes
Create Date: 2026-09-25 13:32:18.451072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd662b83a8c3'
down_revision: Union[str, None] = '20240514_add_incident_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ⚡ Bolt Optimization: Add index for desc(created_at) queries
    op.create_index(op.f('ix_incident_events_created_at'), 'incident_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_evaluation_runs_created_at'), 'evaluation_runs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_evaluation_runs_created_at'), table_name='evaluation_runs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_incident_events_created_at'), table_name='incident_events')
