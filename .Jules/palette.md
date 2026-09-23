## 2024-05-24 - Isolated Loading States & Explicit Error Alerts
**Learning:** Using shared booleans (like `isInvestigating`) for loading states in lists causes all items to appear active simultaneously, confusing users. Furthermore, relying on falsy checks without explicit error rendering swallows API errors silently.
**Action:** Always use unique identifiers (e.g., `investigatingId`) for active states in lists to isolate visual feedback, and explicitly render asynchronous errors in dedicated containers with `role="alert"` so they are announced to screen readers and visible to users.
