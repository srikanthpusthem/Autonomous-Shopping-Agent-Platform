from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Shopping Copilot API"
    app_env: str = "development"
    app_debug: bool = True
    api_port: int = 8000
    database_url: str = "postgresql+psycopg://shopping:shopping@localhost:5432/shopping"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 24 * 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("app_env")
    @classmethod
    def normalize_app_env(cls, value: str) -> str:
        return value.lower().strip()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
