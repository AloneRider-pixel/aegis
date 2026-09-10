## 2024-09-10 - Login Form Accessibility Improvement
**Learning:** React login forms in this template lack proper ARIA alerts for errors and accessible labels linked via `htmlFor`. Default Tailwind inputs are also missing clear focus states.
**Action:** When working on forms, proactively add explicit `<label>` elements linked to input `id`s, ensure error messages have `role="alert"`, and apply `focus:ring` classes for keyboard navigation.
