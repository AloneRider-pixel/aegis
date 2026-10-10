## 2024-10-04 - Unnecessary O(N) Re-renders on List Selection
**Learning:** In React, passing dynamically generated values (like objects or functions that change on every render) or deriving boolean props (like `isSelected`) directly within an inline `map` loop function body will cause every item in the list to re-render when the parent's state changes.
**Action:** Extract list items into separate components wrapped in `React.memo()`, pass primitive boolean flags (like `isSelected={selectedId === item.id}`), and stabilize callback references using `React.useCallback()` to prevent O(N) re-renders.

## 2026-10-10 - Avoid O(N) parsing in sorted append-only arrays
**Learning:** When filtering append-only chronologically sorted arrays by a timestamp threshold, O(N) datetime parsing overhead can be avoided by iterating backwards with `reversed()` and using lexicographical string comparisons on ISO-8601 timestamps (e.g. `iso_str1 < iso_str2`), breaking early when hitting the cutoff.
**Action:** Iterate backwards with `reversed()` and compare ISO strings directly to optimize time-based lookups.
