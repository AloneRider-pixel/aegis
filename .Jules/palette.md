## 2024-05-24 - Shared loading state causes confusing UX
**Learning:** Using a single boolean state (`investigating`) for loading actions in a mapped list causes all items in the list to visually reflect the loading state, confusing users about which item is actually being processed.
**Action:** Always use specific IDs (`investigatingId`, `approvingId`) for state management in lists to ensure loading feedback is localized exclusively to the interacted item.

## 2024-05-25 - Redundant Screen Reader Output on SVGs
**Learning:** Decorative SVG elements (like `Spinner` components) inside interactive buttons are often announced confusingly by screen readers if they lack appropriate ARIA attributes, creating a poor accessible experience.
**Action:** Always add `aria-hidden="true"` to generic/decorative SVG components (like spinners or icons) when the surrounding element (like a button) already provides semantic meaning or text content.
## 2024-10-08 - Dead-end Empty States Need CTAs
**Learning:** Empty states (like "No incidents detected") and success states (like "Scenario Triggered") that simply instruct the user to "Go to X tab" create friction and dead-ends in the UX. Users shouldn't have to hunt for the top navigation to follow instructions.
**Action:** Always provide explicit, actionable Call-to-Action (CTA) buttons directly within empty states or terminal success states to guide the user to the next logical step in their journey without requiring them to rely solely on global navigation.
