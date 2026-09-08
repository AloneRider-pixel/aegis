## 2024-05-24 - Missing Authentication on Core API Endpoints
**Vulnerability:** Found `GET /api/incidents`, `GET /api/incidents/{incident_id}`, `GET /api/services`, and `GET /api/simulator/scenarios` endpoints completely open without any authorization checks, exposing internal state and potential PII.
**Learning:** Developers likely created these routes quickly for UI binding and forgot to add the `user: dict = Depends(get_current_user)` dependency in the function signatures.
**Prevention:** In FastAPI, it is safer to apply authentication globally at the router level (e.g., `app.include_router(incidents_router, dependencies=[Depends(get_current_user)])`) rather than relying on per-endpoint dependency injection which is easy to forget.
