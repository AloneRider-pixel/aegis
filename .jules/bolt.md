## 2024-05-14 - PostgreSQL Foreign Key Missing Indexes
**Learning:** PostgreSQL does not automatically index foreign keys by default, which can result in slow O(N) sequential scans for joins and relationship queries. In the backend SQLAlchemy models, `ForeignKey` references were missing the `index=True` attribute.
**Action:** When adding foreign key relationships in SQLAlchemy models backed by PostgreSQL, explicitly add `index=True` to prevent performance bottlenecks.
## 2024-05-18 - Missing SQLAlchemy Index on Foreign Keys
**Learning:** In SQLAlchemy models, PostgreSQL does not automatically index foreign keys by default, leading to silent O(N) sequential scans during relationship queries or cascading deletes, which creates severe performance bottlenecks as tables grow.
**Action:** When designing or refactoring SQLAlchemy models involving `ForeignKey` constraints, ALWAYS explicitly specify `index=True` for those columns (e.g., `service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), index=True)`) unless you have a specific, measurable reason to avoid the index overhead.
