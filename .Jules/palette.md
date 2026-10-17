## 2024-05-24 - Shared loading state causes confusing UX
**Learning:** Using a single boolean state (`investigating`) for loading actions in a mapped list causes all items in the list to visually reflect the loading state, confusing users about which item is actually being processed.
**Action:** Always use specific IDs (`investigatingId`, `approvingId`) for state management in lists to ensure loading feedback is localized exclusively to the interacted item.

## 2024-05-25 - Redundant Screen Reader Output on SVGs
**Learning:** Decorative SVG elements (like `Spinner` components) inside interactive buttons are often announced confusingly by screen readers if they lack appropriate ARIA attributes, creating a poor accessible experience.
**Action:** Always add `aria-hidden="true"` to generic/decorative SVG components (like spinners or icons) when the surrounding element (like a button) already provides semantic meaning or text content.

## 2026-10-10 - Prevent Master-Detail Dead-ends
**Learning:** In master-detail views (like the incidents dashboard), when a user selects a new item from the master list, any temporary or expanded states associated with the previously selected item (e.g., an AI Investigation Report) MUST be explicitly cleared. Failing to do so creates a UX trap where the new item's details are permanently obscured by the old item's report.
**Action:** Always verify that `onSelect` handlers reset related sibling states, provide accessible "Close" buttons on all overlay/detail panels, and implement global `Escape` key listeners to allow users an intuitive "way out" to the empty state.
## 2026-10-16 - Global Keyboard Shortcuts\n**Learning:** Implementing global `Escape` key listeners in a React SPA provides a huge accessibility and UX boost for dismissing modals or detail panes, but requires careful event management to avoid intercepting inputs or breaking when state changes.\n**Action:** Always check `document.activeElement?.tagName` before firing the dismiss action to ensure users can type in inputs, and keep the `useEffect` dependency array empty by using stable state setter functions (like `setSelected(null)`) to avoid unnecessary re-renders or stale closures.
## 2024-05-24 - Empty State Call-to-Action Buttons
**Learning:** Users often encounter dead-end empty states (like 0 incidents on the dashboard or success states in the simulator) with descriptive text but no actionable navigation, forcing them to manually use the header menu.
**Action:** When designing or updating empty or success states in the UI, always provide explicit, actionable Call-to-Action (CTA) buttons that link directly to the next logical step (e.g., "Go to Simulator" when there are no incidents, or "View in Incidents" after triggering a scenario) to prevent dead-end UX.
