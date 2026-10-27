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
## 2024-05-26 - Dead-end empty states
**Learning:** Empty states without explicit Call-to-Action (CTA) buttons create dead-ends in user journeys, leaving users unsure of how to proceed or what actions are expected of them next.
**Action:** Always provide clear, actionable CTA buttons in empty or terminal UI states to guide users seamlessly toward the next logical step in the application flow.

## 2026-10-18 - Screen Reader Noise from Inline Emojis
**Learning:** Screen readers announce inline text emojis (e.g., "📊 Dashboard") verbatim, which adds auditory clutter and creates a confusing experience for visually impaired users.
**Action:** Always wrap decorative or inline emojis in a `<span aria-hidden="true">` when the adjacent text already conveys the full meaning, ensuring a clean and focused auditory experience.
## 2026-10-27 - Contextual Form Error Announcements
**Learning:** When forms display a generic error message below the inputs (e.g., "Invalid credentials" after a failed login), screen readers will not automatically announce it to the user who might currently be focused on an input field.
**Action:** When adding visual error states to form inputs, always pair them with `aria-invalid="true"` and `aria-describedby` linking directly to the error message container (with `role="alert"`) to ensure screen readers announce the error contextually upon field focus.
