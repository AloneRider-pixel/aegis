## 2024-09-10 - Missing Authentication on Sensitive FastAPI Endpoints
**Vulnerability:** Several sensitive endpoints (`/api/incidents`, `/api/simulator/scenarios`, `/api/services`) were accessible without authentication because they were missing the `Depends(get_current_user)` dependency injection.
**Learning:** In FastAPI, relying on individual route-level dependency injection for authentication can lead to oversights if developers forget to add the dependency to new or existing routes.
**Prevention:** To prevent this, consider applying authentication dependencies at the `APIRouter` level (e.g., `router = APIRouter(dependencies=[Depends(get_current_user)])`) for groups of routes that should all require authentication, rather than relying on per-route injection.
