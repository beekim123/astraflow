from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AstraFlow AI"
    app_env: str = "local"
    service_name: str = "backend-api"
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
    upload_dir: str = "var/uploads"
    upload_image_max_mb: int = 10
    upload_file_max_mb: int = 50
    upload_video_max_mb: int = 200
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: int = 30
    ai_gateway_url: str = "http://127.0.0.1:8010"
    ai_gateway_internal_token: str = "local-dev-token"
    ai_gateway_timeout_seconds: int = 120
    mcp_llm_gateway_url: str = "http://127.0.0.1:8020"
    ark_base_url: str = ""
    ark_api_key: str = ""
    ark_chat_model: str = ""
    ark_embedding_model: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def effective_llm_base_url(self) -> str:
        return self.llm_base_url or self.ark_base_url

    @property
    def effective_llm_api_key(self) -> str:
        return self.llm_api_key or self.ark_api_key

    @property
    def effective_llm_model(self) -> str:
        return self.llm_model or self.ark_chat_model


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
