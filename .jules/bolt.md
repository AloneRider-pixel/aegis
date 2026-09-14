## 2025-02-18 - SQLAlchemy PostgreSQL Foreign Key Missing Index
**Learning:** PostgreSQL does not automatically index foreign keys created by SQLAlchemy models. Traversing relationships caused full sequential scans.
**Action:** Always ensure `index=True` is explicitly specified for `ForeignKey` relationships in SQLAlchemy when building heavily relation-queried endpoints.
