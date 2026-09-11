## 2024-09-11 - Add missing authentication to backend endpoints
**Vulnerability:** Several backend API endpoints (`/api/incidents`, `/api/incidents/{incident_id}`, `/api/simulator/scenarios`, `/api/services`) were missing authentication checks.
**Learning:** FastAPI `Depends` is required to enforce authentication on each endpoint individually; without it, the endpoints are publicly accessible to anyone, which is a critical security vulnerability.
**Prevention:** Always ensure that `Depends(get_current_user)` (or an equivalent authentication dependency) is explicitly added to the signature of all endpoints that require authorization.
