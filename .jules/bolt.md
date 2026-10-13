## 2024-10-04 - Unnecessary O(N) Re-renders on List Selection
**Learning:** In React, passing dynamically generated values (like objects or functions that change on every render) or deriving boolean props (like `isSelected`) directly within an inline `map` loop function body will cause every item in the list to re-render when the parent's state changes.
**Action:** Extract list items into separate components wrapped in `React.memo()`, pass primitive boolean flags (like `isSelected={selectedId === item.id}`), and stabilize callback references using `React.useCallback()` to prevent O(N) re-renders.
## 2024-10-13 - Avoid O(N) array filtering for chronologically appended data
**Learning:** When retrieving recent data (like recent 30 min logs) from append-only chronologically sorted lists, iterating from the start requires O(N) checks and processes the oldest (often irrelevant) data first.
**Action:** Iterate backwards using `reversed()` and lexicographically compare ISO-8601 string timestamps (e.g., `iso_str1 < iso_str2`) to break early as soon as you cross the cutoff threshold, effectively making the search O(1) relative to total history size.
