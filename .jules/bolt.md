## 2026-09-08 - Backend State Issue
**Learning:** The backend has a known broken state with 'Table is already defined' in models during pytest, and a missing Optional import in scenarios.py. It also has conflicting dependencies in requirements.txt (langgraph vs langchain-core). When working on frontend tasks, these should NOT be fixed, as they are out of scope.
**Action:** Do not run backend tests if the PR is focused exclusively on the frontend, or explicitly ignore existing backend errors since they existed prior to the change. Do not attempt to fix unrelated files to make tests pass.
