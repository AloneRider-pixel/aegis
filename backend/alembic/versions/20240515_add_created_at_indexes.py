"""add created_at indexes

Revision ID: 20240515_add_created_at_indexes
Revises: 20240514_add_incident_indexes
Create Date: 2024-05-15 12:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '20240515_add_created_at_indexes'
down_revision = '20240514_add_incident_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f('ix_incident_events_created_at'), 'incident_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_evaluation_runs_created_at'), 'evaluation_runs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_evaluation_runs_created_at'), table_name='evaluation_runs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_incident_events_created_at'), table_name='incident_events')
