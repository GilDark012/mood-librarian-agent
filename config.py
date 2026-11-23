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
    groq_model: str = Field(default="openai/gpt-oss-120b")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1")

    # --- API access control ---
    # If set, callers must send this value in the `X-API-Key` header.
    # If empty, the API is open (intended only for local/demo use).
    api_key: str = Field(default="")
    # Comma-separated list of allowed CORS origins, or "*" for any.
    allowed_origins: str = Field(default="*")
    # SlowAPI per-IP rate limits applied to the agent endpoints.
    rate_limit: str = Field(default="10/minute")
    rate_limit_daily: str = Field(default="200/day")

    # --- Request limits / reliability ---
    max_mood_length: int = Field(default=500, ge=1)
    request_timeout: float = Field(default=30.0, gt=0)
    max_agent_steps: int = Field(default=3, ge=1)
    max_journey_stages: int = Field(default=3, ge=1)

    # --- Statistics ---
    # If set, GET /stats requires this value in the `X-Stats-Token` header
    # (otherwise /stats is disabled and returns 404).
    stats_token: str = Field(default="")
    # Durable counters via Upstash Redis REST (optional). Without these, stats
    # are kept in memory and reset when the instance restarts.
    upstash_redis_rest_url: str = Field(default="")
    upstash_redis_rest_token: str = Field(default="")
    # Rough blended Groq price per 1M tokens, for the cost estimate in /stats.
    cost_per_mtoken_usd: float = Field(default=0.30, ge=0)

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
