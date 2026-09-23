## 2025-05-18 - PostgreSQL Foreign Key Missing Index Bottleneck
**Learning:** PostgreSQL does not automatically index foreign keys like MySQL does. In incident response apps, fetching an incident timeline (e.g. `IncidentEvent` by `incident_id`) is highly frequent and will cause O(N) sequential scans without explicit indices.
**Action:** Always verify that foreign keys in SQLAlchemy (`ForeignKey`) on frequently-queried relations include `index=True` explicitly.
## 2025-02-18 - SQLAlchemy PostgreSQL Foreign Key Missing Index
**Learning:** PostgreSQL does not automatically index foreign keys created by SQLAlchemy models. Traversing relationships caused full sequential scans.
**Action:** Always ensure `index=True` is explicitly specified for `ForeignKey` relationships in SQLAlchemy when building heavily relation-queried endpoints.
## 2024-05-18 - Missing SQLAlchemy Foreign Key Indexes
**Learning:** PostgreSQL does not automatically index foreign keys by default, leading to O(N) sequential scans for relation lookups.
**Action:** Always add `index=True` when defining SQLAlchemy ForeignKey relationships to ensure optimal performance.
## 2024-05-14 - PostgreSQL Foreign Key Missing Indexes
**Learning:** PostgreSQL does not automatically index foreign keys by default, which can result in slow O(N) sequential scans for joins and relationship queries. In the backend SQLAlchemy models, `ForeignKey` references were missing the `index=True` attribute.
**Action:** When adding foreign key relationships in SQLAlchemy models backed by PostgreSQL, explicitly add `index=True` to prevent performance bottlenecks.
## 2024-05-18 - Missing SQLAlchemy Index on Foreign Keys
**Learning:** In SQLAlchemy models, PostgreSQL does not automatically index foreign keys by default, leading to silent O(N) sequential scans during relationship queries or cascading deletes, which creates severe performance bottlenecks as tables grow.
**Action:** When designing or refactoring SQLAlchemy models involving `ForeignKey` constraints, ALWAYS explicitly specify `index=True` for those columns (e.g., `service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), index=True)`) unless you have a specific, measurable reason to avoid the index overhead.
## 2026-09-23 - Alembic Logging KeyError
**Learning:** When running Alembic migrations, `fileConfig(config.config_file_name)` in `env.py` can throw a `KeyError: 'formatters'` if logging is not fully configured in `alembic.ini`.
**Action:** When working in repositories with minimal Alembic configurations, always wrap the `fileConfig` call in `env.py` with a `try-except KeyError` block to prevent migration script generation and execution from failing.
