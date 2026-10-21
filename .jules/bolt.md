## 2026-10-14 - Timestamp Ordering in Telemetry Stores
**Learning:** Telemetry arrays are not uniformly ordered by timestamp: scenario metrics may append older anomaly samples after newer baseline samples, and generated logs can receive randomized timestamps. A reverse scan that stops at the first stale entry can omit valid recent telemetry.
**Action:** Use ISO timestamp comparisons to avoid repeated datetime parsing. Only use early termination when chronological append order is a guaranteed invariant; otherwise continue filtering every entry or introduce an explicitly ordered index. Keep out-of-order timestamp regressions in the test suite.
## 2026-10-15 - FastAPI CPU Blocking with Bcrypt
**Learning:** Synchronous CPU-bound operations like `bcrypt.checkpw` (used in `verify_password`) block the asynchronous event loop in FastAPI when called directly inside an `async def` endpoint. This severely degrades concurrent request handling.
**Action:** Always offload expensive synchronous hashing/cryptography functions using `fastapi.concurrency.run_in_threadpool` to free up the main event loop.
