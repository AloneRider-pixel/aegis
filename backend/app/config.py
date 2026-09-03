"""
Aegis Configuration — all settings from environment variables.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    app_name: str = "aegis"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me"

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "aegis"
    postgres_user: str = "aegis_user"
    postgres_password: str = "aegis_password"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    local_model_url: str = "http://localhost:11434"

    # AI Safety
    max_agent_iterations: int = 15
    max_token_budget: int = 50000
    max_tool_calls: int = 20
    max_investigation_seconds: int = 300

    # Auth
    jwt_secret_key: str = "jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Frontend
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
