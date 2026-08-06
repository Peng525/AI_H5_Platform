"""应用配置（从环境变量读取）。"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_ROOT.parent


def _env_files() -> tuple[str, ...]:
    """backend/.env 与项目根 .env（Docker 挂载 ../.env）均尝试加载。"""
    candidates = (_BACKEND_ROOT / ".env", _PROJECT_ROOT / ".env")
    existing = tuple(str(p) for p in candidates if p.is_file())
    return existing or (".env",)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
    jwt_expire_hours: int = 168
    free_quota_per_user: int = 5

    # 人机验证：mock（仅开发）| tencent
    captcha_provider: str = "mock"
    tencent_captcha_app_id: str = ""
    tencent_captcha_app_secret_key: str = ""
    tencent_secret_id: str = ""
    tencent_secret_key: str = ""

    # 短信：mock（仅开发）| tencent
    sms_provider: str = "mock"
    tencent_sms_sdk_app_id: str = ""
    tencent_sms_sign_name: str = ""
    tencent_sms_template_id: str = ""
    tencent_sms_region: str = "ap-guangzhou"
    sms_code_ttl_minutes: int = 5
    sms_send_cooldown_seconds: int = 60
    sms_daily_limit_per_phone: int = 10

    # 微信支付 Native（API v3）
    wechat_pay_mch_id: str = ""
    wechat_pay_app_id: str = ""
    wechat_pay_api_v3_key: str = ""
    wechat_pay_serial_no: str = ""
    wechat_pay_private_key_path: str = "./certs/apiclient_key.pem"
    wechat_pay_notify_url: str = ""

    # 逗号分隔的管理员账号（与 users.username 匹配，须在 .env 中配置）
    admin_usernames: str = ""

    # 可选：首次启动时创建种子用户（仅自建环境，勿写入公开文档）
    seed_demo_username: str = ""
    seed_demo_password: str = ""
    seed_admin_username: str = ""
    seed_admin_password: str = ""

    env_persist_path: str = "../.env"

    # 微信个人收款码（本地）：图片 URL 或 /static/wechat-pay-qr.png
    wechat_personal_qr_url: str = "/static/wechat-pay-qr.png"

    # 待支付订单有效时长（分钟），超时自动作废
    order_pending_expire_minutes: int = 2

    # 中转 API 充值链接（管理端仅展示外链，推理令牌不查余额）
    relay_quota_profile: str = "newapi"
    relay_quota_api_url: str = ""
    relay_quota_low_threshold: float = 1.0
    relay_quota_low_cny: float = 5.0
    relay_dashboard_recharge_url: str = ""
    relay_quota_usd_divisor: float = 500000.0
    relay_quota_cny_divisor: float = 500000.0
    # NovAI 控制台与 API 可能不同域（如 once-cf.novai.su 钱包 + us.novaiapi.com 调用）
    relay_novai_dashboard_url: str = ""

    # Resume module (English API /api/v1/resume/*)
    resume_max_per_user: int = 5
    resume_max_file_mb: int = 5
    resume_retention_days: int = 30
    resume_data_dir: str = "./data/resume"
    resume_paddleocr_enabled: bool = False
    resume_paddleocr_lang: str = "ch"

    # ppt-master 子项目根目录（默认 develop/ppt-master-main）
    ppt_master_root: str = ""
    ppt_master_workspace: str = "./data/ppt_master_projects"
    ppt_master_max_concurrent: int = 1
    ppt_master_skip_images: bool = True
    ppt_master_job_timeout_sec: float = 1800.0
    imported_deck_templates_dir: str = "./data/imported_deck_templates"


settings = Settings()
