## 2024-09-12 - Form Accessibility Needs Explicit Labels
**Learning:** Even when inputs have descriptive placeholders, screen readers still need explicit `label` elements tied via `htmlFor` and `id` to function correctly.
**Action:** Always add `sr-only` labels if visible labels conflict with the design, ensuring forms are structurally accessible without altering aesthetics.
## 2026-09-07 - Login Form Accessibility Improvement
**Learning:** Using `isLoggingIn` state is critical for disabling inputs/buttons, providing visual feedback, and preventing duplicate submissions during async actions in React forms. In addition, associating labels properly and using `role="alert"` for errors is crucial for basic keyboard/screen-reader accessibility on generic form components.
**Action:** Ensure all standard login/registration forms implement these accessibility defaults as standard practice for basic inclusive UX design.
