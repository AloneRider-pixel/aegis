## 2026-10-14 - Timestamp Ordering in Telemetry Stores
**Learning:** Telemetry arrays are not uniformly ordered by timestamp: scenario metrics may append older anomaly samples after newer baseline samples, and generated logs can receive randomized timestamps. A reverse scan that stops at the first stale entry can omit valid recent telemetry.
**Action:** Use ISO timestamp comparisons to avoid repeated datetime parsing. Only use early termination when chronological append order is a guaranteed invariant; otherwise continue filtering every entry or introduce an explicitly ordered index. Keep out-of-order timestamp regressions in the test suite.
## 2023-10-24 - Async Event Loop Blocking from bcrypt
**Learning:** Synchronous CPU-bound operations (like `bcrypt.checkpw`) inside FastAPI `async def` endpoints block the main event loop, severely impacting concurrent request throughput.
**Action:** Offload CPU-bound cryptographic operations to a separate thread using `fastapi.concurrency.run_in_threadpool`.
