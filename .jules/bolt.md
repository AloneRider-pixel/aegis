## 2024-10-09 - Telemetry Log Parsing Overhead
**Learning:** In append-only in-memory stores that chronologically insert telemetry with ISO-8601 timestamps, parsing `datetime` strings and sequentially iterating over the entire array for recent items causes an O(N) performance bottleneck.
**Action:** When filtering for recent logs in chronologically sorted append-only stores, iterate backward using `reversed()` and compare raw ISO-8601 timestamp strings directly against an ISO cutoff string. Break early on the first out-of-bounds match.
