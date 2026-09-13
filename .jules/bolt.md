## 2024-05-14 - PostgreSQL Foreign Key Missing Indexes
**Learning:** PostgreSQL does not automatically index foreign keys by default, which can result in slow O(N) sequential scans for joins and relationship queries. In the backend SQLAlchemy models, `ForeignKey` references were missing the `index=True` attribute.
**Action:** When adding foreign key relationships in SQLAlchemy models backed by PostgreSQL, explicitly add `index=True` to prevent performance bottlenecks.
