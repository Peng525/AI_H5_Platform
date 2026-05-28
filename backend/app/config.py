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
    # 未指定 tier 时的兜底（与免费档一致）
    llm_relay_model: str = "gemini-3.1-flash-image-preview"

    llm_official_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    llm_official_api_key: str = ""
    llm_official_model: str = "gemini-3.1-flash-image-preview"

    # 会员档位模型（NovAI 等中转常用 -image-preview 后缀）
    llm_model_free: str = "gemini-3.1-flash-image-preview"
    llm_model_pro: str = "gemini-3-pro-image-preview"
    llm_image_model_free: str = "gemini-3.1-flash-image-preview"
    llm_image_model_pro: str = "gemini-3-pro-image-preview"

    jwt_secret: str = "dev-change-me-in-production"
    jwt_algorithm: str = "HS256"
    free_quota_per_user: int = 5

    # 逗号分隔的管理员账号（与 users.username 匹配）
    admin_usernames: str = "admin@ai-h5.com"
    # .env 持久化路径（Docker 内建议 /app/.env）
    env_persist_path: str = "../.env"


settings = Settings()
