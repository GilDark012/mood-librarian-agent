"""Centralised, typed application configuration.

Loads settings from environment variables and a local `.env` file (never
committed). Import `settings` anywhere you need configuration.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM (Groq, OpenAI-compatible endpoint) ---
    groq_api_key: str = Field(default="", description="Groq API key.")
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1")

    # --- API access control ---
    # If set, callers must send this value in the `X-API-Key` header.
    # If empty, the API is open (intended only for local/demo use).
    api_key: str = Field(default="")
    # Comma-separated list of allowed CORS origins, or "*" for any.
    allowed_origins: str = Field(default="*")
    # SlowAPI rate limit applied to /recommend, e.g. "10/minute".
    rate_limit: str = Field(default="10/minute")

    # --- Request limits / reliability ---
    max_mood_length: int = Field(default=500, ge=1)
    request_timeout: float = Field(default=30.0, gt=0)
    max_agent_steps: int = Field(default=5, ge=1)

    @property
    def origins_list(self) -> list[str]:
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
