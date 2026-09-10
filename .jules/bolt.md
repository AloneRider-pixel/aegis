## 2025-05-18 - PostgreSQL Foreign Key Missing Index Bottleneck
**Learning:** PostgreSQL does not automatically index foreign keys like MySQL does. In incident response apps, fetching an incident timeline (e.g. `IncidentEvent` by `incident_id`) is highly frequent and will cause O(N) sequential scans without explicit indices.
**Action:** Always verify that foreign keys in SQLAlchemy (`ForeignKey`) on frequently-queried relations include `index=True` explicitly.
