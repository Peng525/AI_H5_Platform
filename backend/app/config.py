"""应用配置（从环境变量读取）。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI智能H5演示平台"
    app_port: int = 8080
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # auto | relay | official
    llm_default_channel: str = "auto"
    llm_auto_order: str = "official,relay"
    llm_timeout: float = 120.0

    llm_relay_base_url: str = ""
    llm_relay_api_key: str = ""
    llm_relay_model: str = "gpt-4o-mini"

    llm_official_base_url: str = "https://api.openai.com/v1"
    llm_official_api_key: str = ""
    llm_official_model: str = "gpt-4o-mini"

    jwt_secret: str = "dev-change-me-in-production"
    jwt_algorithm: str = "HS256"
    free_quota_per_user: int = 5


settings = Settings()
