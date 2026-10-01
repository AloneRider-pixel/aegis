## 2024-05-24 - Shared loading state causes confusing UX
**Learning:** Using a single boolean state (`investigating`) for loading actions in a mapped list causes all items in the list to visually reflect the loading state, confusing users about which item is actually being processed.
**Action:** Always use specific IDs (`investigatingId`, `approvingId`) for state management in lists to ensure loading feedback is localized exclusively to the interacted item.

## 2026-10-01 - Silent API failures cause false-positive success states
**Learning:** In asynchronous components (like Dashboard lists), silently catching fetch errors without storing them can trick the UI into thinking the data is simply empty. This triggers empty state "success" messages instead of alerting the user that a failure occurred.
**Action:** Always implement explicit error state boundaries when fetching data and ensure the resulting error UI is accessible using `role="alert"`.
