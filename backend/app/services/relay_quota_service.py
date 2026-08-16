"""中转平台充值链接（余额需在站点控制台自行查看）。"""
from dataclasses import dataclass
from urllib.parse import urlparse

from app.config import get_llm_provider, settings
from app.services.llm.provider import _relay_ready


@dataclass
class RelayLinkInfo:
    recharge_url: str
    configured: bool
    message: str


def _novai_dashboard_origin() -> str:
    explicit = settings.relay_novai_dashboard_url.strip().rstrip("/")
    if explicit:
        return explicit
    recharge = settings.relay_dashboard_recharge_url.strip()
    if recharge:
        parsed = urlparse(recharge)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    return "https://once-cf.novai.su"


def _is_novai_profile(profile: str) -> bool:
    if profile == "novai":
        return True
    haystack = " ".join(
        [
            (get_llm_provider("relay") or {}).get("base_url", "").lower(),
            settings.relay_novai_dashboard_url.lower(),
            settings.relay_dashboard_recharge_url.lower(),
        ]
    )
    return "novai" in haystack


def _effective_profile() -> str:
    profile = settings.relay_quota_profile.lower()
    if profile == "novai" or _is_novai_profile(profile):
        return "novai"
    return profile


def _origin_from_relay_base() -> str:
    base = (get_llm_provider("relay") or {}).get("base_url", "").strip().rstrip("/")
    if not base:
        return ""
    parsed = urlparse(base)
    return f"{parsed.scheme}://{parsed.netloc}"


def _resolve_recharge_url(profile: str) -> str:
    if settings.relay_dashboard_recharge_url.strip():
        return settings.relay_dashboard_recharge_url.strip()
    if profile == "novai":
        dash = _novai_dashboard_origin()
        return f"{dash}/wallet"
    origin = _origin_from_relay_base()
    if origin:
        return f"{origin}/topup"
    return ""


def get_relay_recharge_link() -> RelayLinkInfo:
    if not _relay_ready():
        return RelayLinkInfo(
            recharge_url="",
            configured=False,
            message="未配置中转 API（LLM_RELAY_BASE_URL / LLM_RELAY_API_KEY）",
        )
    url = _resolve_recharge_url(_effective_profile())
    if not url:
        return RelayLinkInfo(
            recharge_url="",
            configured=False,
            message="未配置充值链接，请设置 RELAY_DASHBOARD_RECHARGE_URL",
        )
    return RelayLinkInfo(
        recharge_url=url,
        configured=True,
        message="推理令牌无法自动读取余额，请登录中转平台控制台查看并充值",
    )
