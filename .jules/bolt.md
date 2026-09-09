## 2024-05-14 - Missing Indexes in Incident Queries
**Learning:** `list_incidents` filters heavily on `status`, `severity`, and sorts by `created_at` in the `Incident` table but was lacking database indexes.
**Action:** Adding indexes to `status`, `severity`, and `created_at` to improve read latency for list and filter queries.
