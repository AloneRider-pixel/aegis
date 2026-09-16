## 2023-10-27 - Insecure Default Configuration
**Vulnerability:** Hardcoded `secret_key` and `jwt_secret_key` in `backend/app/config.py`.
**Learning:** Default fallback values for security keys were used which could easily make it to production environments, especially since Pydantic BaseSettings falls back to the default when an environment variable isn't set.
**Prevention:** Remove default values for sensitive configuration options in Pydantic Settings classes to force failure if they are not provided via environment variables.
