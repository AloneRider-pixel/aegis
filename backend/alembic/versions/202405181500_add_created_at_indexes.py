"""Add index to created_at in AuditLog and EvaluationRun

Revision ID: 202405181500
Revises:
Create Date: 2024-05-18 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '202405181500'
down_revision: Union[str, None] = '20240514_add_incident_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ⚡ Bolt Optimization: Add index to desc(AuditLog.created_at) queries
    op.create_index(
        op.f('ix_audit_logs_created_at'),
        'audit_logs',
        ['created_at'],
        unique=False
    )
    # ⚡ Bolt Optimization: Add index to desc(EvaluationRun.created_at) queries
    op.create_index(
        op.f('ix_evaluation_runs_created_at'),
        'evaluation_runs',
        ['created_at'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_evaluation_runs_created_at'), table_name='evaluation_runs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
