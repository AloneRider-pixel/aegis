## 2024-05-18 - Missing SQLAlchemy Foreign Key Indexes
**Learning:** PostgreSQL does not automatically index foreign keys by default, leading to O(N) sequential scans for relation lookups.
**Action:** Always add `index=True` when defining SQLAlchemy ForeignKey relationships to ensure optimal performance.
