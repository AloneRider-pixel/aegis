## 2024-05-24 - [CRITICAL] Hardcoded Password in Initial Admin User Creation
**Vulnerability:** Found a hardcoded password `admin123` used for creating the initial admin user during the FastAPI application lifespan setup in `backend/app/main.py`.
**Learning:** Hardcoded credentials within the application startup sequence bypass dynamic configuration, leaving production systems vulnerable to using weak, discoverable default passwords.
**Prevention:** Always rely on environment-driven configuration (e.g., using `pydantic-settings` to retrieve values) for all sensitive values like initial passwords, API keys, and database connections. Provide secure defaults but make them easily overridable via `.env`.
