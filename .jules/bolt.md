## 2026-10-14 - Timestamp Ordering in Telemetry Stores
**Learning:** Telemetry arrays are not uniformly ordered by timestamp: scenario metrics may append older anomaly samples after newer baseline samples, and generated logs can receive randomized timestamps. A reverse scan that stops at the first stale entry can omit valid recent telemetry.
**Action:** Use ISO timestamp comparisons to avoid repeated datetime parsing. Only use early termination when chronological append order is a guaranteed invariant; otherwise continue filtering every entry or introduce an explicitly ordered index. Keep out-of-order timestamp regressions in the test suite.
## 2026-10-17 - Array map memoization
**Learning:** Mapping complex lists using inline elements with inline callbacks passed to onClick can trigger full list re-renders (O(N)) anytime any variable in the component updates (e.g. updating a loading state or triggering state).
**Action:** Extract list items into their own components wrapped in `React.memo` and wrap callbacks like `trigger` using `React.useCallback` to achieve O(1) rendering updates when state such as `isTriggering` changes for an individual item.
## 2023-10-24 - Async Event Loop Blocking from bcrypt
**Learning:** Synchronous CPU-bound operations (like `bcrypt.checkpw`) inside FastAPI `async def` endpoints block the main event loop, severely impacting concurrent request throughput.
**Action:** Offload CPU-bound cryptographic operations to a separate thread using `fastapi.concurrency.run_in_threadpool`.
