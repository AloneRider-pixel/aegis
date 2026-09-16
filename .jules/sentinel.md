## 2024-03-05 - Auth Bypass on Sensitive Endpoints
**Vulnerability:** Several endpoints like `/api/incidents`, `/api/incidents/{incident_id}`, `/api/simulator/scenarios`, and `/api/services` lack authentication, allowing any unauthenticated user to access sensitive operations data and potentially trigger incidents.
**Learning:** In FastAPI, relying merely on `Depends(get_db)` does not implicitly protect an endpoint. Authentication dependencies (e.g. `user: dict = Depends(get_current_user)`) must be explicitly declared on every endpoint requiring authorization.
**Prevention:** Create a systemic approach to route protection, perhaps using FastAPI router dependencies for grouped routes or writing custom linters/tests that check for unauthenticated routes against a whitelist.
## 2023-10-27 - Insecure Default Configuration
**Vulnerability:** Hardcoded `secret_key` and `jwt_secret_key` in `backend/app/config.py`.
**Learning:** Default fallback values for security keys were used which could easily make it to production environments, especially since Pydantic BaseSettings falls back to the default when an environment variable isn't set.
**Prevention:** Remove default values for sensitive configuration options in Pydantic Settings classes to force failure if they are not provided via environment variables.
