## 2024-10-04 - Unnecessary O(N) Re-renders on List Selection
**Learning:** In React, passing dynamically generated values (like objects or functions that change on every render) or deriving boolean props (like `isSelected`) directly within an inline `map` loop function body will cause every item in the list to re-render when the parent's state changes.
**Action:** Extract list items into separate components wrapped in `React.memo()`, pass primitive boolean flags (like `isSelected={selectedId === item.id}`), and stabilize callback references using `React.useCallback()` to prevent O(N) re-renders.
## 2024-10-09 - O(N) Date Parsing to O(1) String Comparison for Chronological Logs
**Learning:** In append-only, chronologically sorted telemetry/log arrays, fetching the "last N minutes" with a forward loop and `datetime.fromisoformat()` parsing is an expensive O(N) operation.
**Action:** Always use a reverse loop (`reversed()`) and leverage ISO-8601 string lexicographical sorting (`str1 < str2`) to immediately `break` when hitting the cutoff. This transforms the operation from an O(N) date-parsing bottleneck into a near-instant O(1) string comparison.
