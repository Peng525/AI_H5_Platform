"""支付相关 URL 解析。"""
from app.config import settings


def wechat_qr_path() -> str:
    return (settings.wechat_personal_qr_url or "/static/wechat-pay-qr.png").strip()


def absolutize_url(url: str | None, base_url: str | None = None) -> str | None:
    if not url:
        return None
    if url.startswith(("http://", "https://", "weixin://", "data:")):
        return url
    if not base_url:
        return url
    base = base_url.rstrip("/")
    return f"{base}{url}" if url.startswith("/") else f"{base}/{url}"
