## 2024-05-14 - Missing Indexes in Incident Queries
**Learning:** `list_incidents` filters heavily on `status`, `severity`, and sorts by `created_at` in the `Incident` table but was lacking database indexes.
**Action:** Adding indexes to `status`, `severity`, and `created_at` to improve read latency for list and filter queries.

## 2024-05-14 - Dependency conflict in pip install
**Learning:** `langgraph>=0.2.0` and `langchain-core>=0.2.0` have conflicting sub-dependencies that result in "ResolutionImpossible" or "resolution-too-deep" when using `pip install` without bounds, due to version mismatch limits on `langchain-core` coming from `langgraph`.
**Action:** Do not attempt to fix out-of-scope backend CI failure due to the constraints of the performance (Bolt) persona. Ensure PR isolations are maintained strictly to the scoped performance goal, ignoring broader CI issues.
