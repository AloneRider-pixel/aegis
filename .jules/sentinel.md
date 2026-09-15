## 2025-02-28 - Missing Authentication on Sensitive API Endpoints
**Vulnerability:** Found unauthenticated endpoints `/api/incidents`, `/api/incidents/{incident_id}`, `/api/services`, and `/api/simulator/scenarios` exposing internal operational data.
**Learning:** These endpoints likely lacked authentication during initial development for ease of testing or oversight. Relying solely on `Depends(get_db)` does not implicitly protect an endpoint; authentication dependencies must be explicitly declared on every route.
**Prevention:** Always verify that every sensitive route is explicitly protected by an authentication dependency, like `Depends(get_current_user)`, and validate access controls during route definition.
