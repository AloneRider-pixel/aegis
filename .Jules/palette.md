## 2024-05-24 - React useEffect Async Warning
**Learning:** When refactoring a synchronous data-fetching function to `async/await` in React components, directly passing it to `useEffect` (e.g., `useEffect(loadIncidents, [])`) triggers a React warning and potential memory leaks because `useEffect` expects a cleanup function, not a Promise.
**Action:** Always wrap `async` functions passed to `useEffect` inside an anonymous synchronous function: `useEffect(() => { loadIncidents() }, [])`.
