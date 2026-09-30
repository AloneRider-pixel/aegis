## 2024-05-24 - React.memo on mapped array items
**Learning:** Extracting complex elements from a list into a dedicated component and using `React.memo` paired with `React.useCallback` in the parent prevents unnecessary re-rendering of every list item when parent state updates.
**Action:** Use this pattern whenever mapping lists where state changes impact one or a few items but not the entire list.
