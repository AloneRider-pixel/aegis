"""add incident indexes

Revision ID: 20240514_add_incident_indexes
Revises:
Create Date: 2024-05-14 12:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '20240514_add_incident_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f('ix_incidents_status'), 'incidents', ['status'], unique=False)
    op.create_index(op.f('ix_incidents_severity'), 'incidents', ['severity'], unique=False)
    op.create_index(op.f('ix_incidents_created_at'), 'incidents', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incidents_created_at'), table_name='incidents')
    op.drop_index(op.f('ix_incidents_severity'), table_name='incidents')
    op.drop_index(op.f('ix_incidents_status'), table_name='incidents')
