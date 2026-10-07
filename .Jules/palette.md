## 2024-05-24 - Shared loading state causes confusing UX
**Learning:** Using a single boolean state (`investigating`) for loading actions in a mapped list causes all items in the list to visually reflect the loading state, confusing users about which item is actually being processed.
**Action:** Always use specific IDs (`investigatingId`, `approvingId`) for state management in lists to ensure loading feedback is localized exclusively to the interacted item.

## 2024-05-25 - Redundant Screen Reader Output on SVGs
**Learning:** Decorative SVG elements (like `Spinner` components) inside interactive buttons are often announced confusingly by screen readers if they lack appropriate ARIA attributes, creating a poor accessible experience.
**Action:** Always add `aria-hidden="true"` to generic/decorative SVG components (like spinners or icons) when the surrounding element (like a button) already provides semantic meaning or text content.
## 2026-10-07 - Empty State CTAs
**Learning:** Empty states without explicit navigation actions (dead-ends) create user friction. Users must manually find the navigation bar to proceed based on text instructions alone.
**Action:** Always provide an explicit, actionable Call-to-Action (CTA) button within empty states that directly routes the user to the required next step, preventing dead-end UX.
