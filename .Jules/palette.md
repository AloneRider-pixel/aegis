## 2025-02-23 - Independent Loading States for Lists
**Learning:** Using a single global boolean (`isInvestigating`) for a list of items causes a confusing UX where clicking one item disables and shows loading text for *all* items in the list. Additionally, swallowed/silent API errors prevent users from taking corrective action.
**Action:** Always map loading states to unique identifiers (e.g., `investigatingId`) instead of booleans when rendering lists, and explicitly render error payloads via `role="alert"` containers.
