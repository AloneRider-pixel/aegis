## 2024-05-24 - Missing Authentication on Core API Endpoints
**Vulnerability:** Found `GET /api/incidents`, `GET /api/incidents/{incident_id}`, `GET /api/services`, and `GET /api/simulator/scenarios` endpoints completely open without any authorization checks, exposing internal state and potential PII.
**Learning:** Developers likely created these routes quickly for UI binding and forgot to add the `user: dict = Depends(get_current_user)` dependency in the function signatures.
**Prevention:** In FastAPI, it is safer to apply authentication globally at the router level (e.g., `app.include_router(incidents_router, dependencies=[Depends(get_current_user)])`) rather than relying on per-endpoint dependency injection which is easy to forget.
## 2024-05-24 - CI Database Credentials Missing
**Vulnerability:** CI workflow failed to run tests because the test step did not provide the required `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, or `DEFAULT_ADMIN_PASSWORD` environment variables. This caused the application config (pydantic base settings) to crash with a validation error or database connection failure.
**Learning:** Even securely built apps that enforce strict environmental config loading will fail if CI tests omit mock/test credentials.
**Prevention:** Always verify test workflows (`.github/workflows/ci.yml`) explicitly pass mock env variables matching the backend configuration schemas for local and CI test execution.
