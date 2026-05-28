"""中转 API 账户额度查询（NewAPI / Novita 等）。"""
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.services.llm.provider import _relay_ready


class RelayQuotaError(Exception):
    pass


@dataclass
class RelayQuotaInfo:
    profile: str
    remaining_raw: float
    remaining_label: str
    remaining_usd: float | None
    used_raw: float | None
    request_count: int | None
    is_low: bool
    low_threshold_usd: float
    recharge_url: str
    message: str


def _origin_from_relay_base() -> str:
    base = settings.llm_relay_base_url.strip().rstrip("/")
    if not base:
        return ""
    parsed = urlparse(base)
    return f"{parsed.scheme}://{parsed.netloc}"


def _novai_dashboard_origin() -> str:
    explicit = settings.relay_novai_dashboard_url.strip().rstrip("/")
    if explicit:
        return explicit
    recharge = settings.relay_dashboard_recharge_url.strip()
    if recharge:
        parsed = urlparse(recharge)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    return ""


def _resolve_quota_url() -> str:
    if settings.relay_quota_api_url.strip():
        return settings.relay_quota_api_url.strip()
    profile = settings.relay_quota_profile.lower()
    if profile == "novita":
        return "https://api.novita.ai/v3/openai/user/balance"
    if profile == "novai":
        dash = _novai_dashboard_origin()
        if dash:
            return f"{dash}/api/user/self"
    origin = _origin_from_relay_base()
    if origin:
        return f"{origin}/api/user/self"
    return ""


def _resolve_recharge_url() -> str:
    if settings.relay_dashboard_recharge_url.strip():
        return settings.relay_dashboard_recharge_url.strip()
    profile = settings.relay_quota_profile.lower()
    if profile == "novai":
        dash = _novai_dashboard_origin()
        if dash:
            return f"{dash}/wallet"
    origin = _origin_from_relay_base()
    if origin:
        return f"{origin}/topup"
    return ""


async def fetch_relay_quota() -> RelayQuotaInfo:
    if not _relay_ready():
        raise RelayQuotaError("未配置 LLM_RELAY_BASE_URL 与 LLM_RELAY_API_KEY")

    url = _resolve_quota_url()
    if not url:
        raise RelayQuotaError("无法解析额度查询地址，请设置 RELAY_QUOTA_API_URL")

    profile = settings.relay_quota_profile.lower()
    headers = {
        "Authorization": f"Bearer {settings.llm_relay_api_key.strip()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=headers)
    except httpx.HTTPError as exc:
        raise RelayQuotaError(f"额度查询网络失败：{exc}") from exc

    if resp.status_code >= 400:
        raise RelayQuotaError(f"额度查询失败 ({resp.status_code})：{resp.text[:300]}")

    try:
        payload = resp.json()
    except ValueError as exc:
        raise RelayQuotaError("额度接口返回非 JSON") from exc

    remaining_raw = 0.0
    used_raw = None
    request_count = None
    remaining_usd = None
    remaining_label = ""

    if profile == "novita":
        credits = float(payload.get("credits") or payload.get("balance") or 0)
        remaining_raw = credits
        remaining_usd = credits * 0.0001
        remaining_label = f"{credits:.0f} 信用点（≈ ${remaining_usd:.2f}）"
    else:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        quota = float(data.get("quota") or 0)
        used = data.get("used_quota")
        remaining_raw = quota
        used_raw = float(used) if used is not None else None
        request_count = data.get("request_count")
        divisor = settings.relay_quota_usd_divisor or 500000.0
        remaining_usd = quota / divisor if divisor else None
        if remaining_usd is not None:
            remaining_label = f"剩余 {quota:.0f} 额度（≈ ${remaining_usd:.2f}）"
        else:
            remaining_label = f"剩余 {quota:.0f} 额度"

    threshold = settings.relay_quota_low_threshold
    is_low = remaining_usd is not None and remaining_usd < threshold
    recharge_url = _resolve_recharge_url()

    if is_low:
        msg = f"中转 API 余额偏低（低于 ${threshold:.2f}），收到微信收款后请尽快充值中转平台"
    else:
        msg = "中转 API 余额正常"

    return RelayQuotaInfo(
        profile=profile,
        remaining_raw=remaining_raw,
        remaining_label=remaining_label,
        remaining_usd=remaining_usd,
        used_raw=used_raw,
        request_count=int(request_count) if request_count is not None else None,
        is_low=is_low,
        low_threshold_usd=threshold,
        recharge_url=recharge_url,
        message=msg,
    )
