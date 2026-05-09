from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AstraFlow AI"
    app_env: str = "local"
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    display_timezone: str = "Asia/Shanghai"
    secret_key: str = Field(default="dev-only-secret")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    database_url: str = "postgresql+asyncpg://astraflow:astraflow@localhost:15432/astraflow"
    redis_url: str = "redis://localhost:16379/0"
    cors_origins: str = (
        "http://localhost:17300,http://localhost:17301,http://localhost:17302,"
        "http://localhost:17303,http://localhost:17304,http://localhost:17305,"
        "http://localhost:17306,http://localhost:18000"
    )
    gate_cookie_secure: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
