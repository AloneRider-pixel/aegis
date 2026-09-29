"""add incident_event created_at index

Revision ID: 20240928_add_incident_event_created_at_index
Revises: 20240514_add_incident_indexes
Create Date: 2024-09-28 12:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '20240928_add_incident_event_created_at_index'
down_revision = '20240514_add_incident_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ⚡ Bolt Optimization: Added index=True to speed up desc(IncidentEvent.created_at) sorting in get_incident_events
    op.create_index(op.f('ix_incident_events_created_at'), 'incident_events', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incident_events_created_at'), table_name='incident_events')
