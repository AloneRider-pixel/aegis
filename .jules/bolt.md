## 2026-10-14 - Timestamp Ordering in Telemetry Stores
**Learning:** Telemetry arrays are not uniformly ordered by timestamp: scenario metrics may append older anomaly samples after newer baseline samples, and generated logs can receive randomized timestamps. A reverse scan that stops at the first stale entry can omit valid recent telemetry.
**Action:** Use ISO timestamp comparisons to avoid repeated datetime parsing. Only use early termination when chronological append order is a guaranteed invariant; otherwise continue filtering every entry or introduce an explicitly ordered index. Keep out-of-order timestamp regressions in the test suite.

## 2025-02-27 - Backend Password Verification Blocks Event Loop
**Learning:** `bcrypt.checkpw` is a synchronous CPU-bound operation. Calling it directly within an `async def` FastAPI endpoint (like login) blocks the main thread, preventing the asyncio event loop from serving concurrent requests (such as health checks) during the ~300ms verification.
**Action:** Use `fastapi.concurrency.run_in_threadpool` to offload synchronous, blocking CPU-bound tasks like `bcrypt.checkpw` to a thread pool when working within `async def` routes, maintaining application responsiveness.
