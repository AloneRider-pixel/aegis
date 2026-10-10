## 2024-05-24 - Shared loading state causes confusing UX
**Learning:** Using a single boolean state (`investigating`) for loading actions in a mapped list causes all items in the list to visually reflect the loading state, confusing users about which item is actually being processed.
**Action:** Always use specific IDs (`investigatingId`, `approvingId`) for state management in lists to ensure loading feedback is localized exclusively to the interacted item.

## 2024-05-25 - Redundant Screen Reader Output on SVGs
**Learning:** Decorative SVG elements (like `Spinner` components) inside interactive buttons are often announced confusingly by screen readers if they lack appropriate ARIA attributes, creating a poor accessible experience.
**Action:** Always add `aria-hidden="true"` to generic/decorative SVG components (like spinners or icons) when the surrounding element (like a button) already provides semantic meaning or text content.

## 2026-10-10 - Prevent Master-Detail Dead-ends
**Learning:** In master-detail views (like the incidents dashboard), when a user selects a new item from the master list, any temporary or expanded states associated with the previously selected item (e.g., an AI Investigation Report) MUST be explicitly cleared. Failing to do so creates a UX trap where the new item's details are permanently obscured by the old item's report.
**Action:** Always verify that `onSelect` handlers reset related sibling states, provide accessible "Close" buttons on all overlay/detail panels, and implement global `Escape` key listeners to allow users an intuitive "way out" to the empty state.
