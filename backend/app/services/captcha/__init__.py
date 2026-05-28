from app.config import settings
from app.services.captcha.base import CaptchaError, CaptchaProvider
from app.services.captcha.mock import MockCaptchaProvider
from app.services.captcha.tencent_captcha import TencentCaptchaProvider

_PROVIDERS: dict[str, CaptchaProvider] = {
    "mock": MockCaptchaProvider(),
    "tencent": TencentCaptchaProvider(),
}


def get_captcha_provider() -> CaptchaProvider:
    name = (settings.captcha_provider or "mock").strip().lower()
    provider = _PROVIDERS.get(name)
    if not provider:
        raise CaptchaError(f"未知验证码提供商：{name}")
    return provider


async def verify_captcha_ticket(ticket: str, randstr: str, user_ip: str) -> None:
    provider = get_captcha_provider()
    ok = await provider.verify_ticket(ticket, randstr, user_ip)
    if not ok:
        raise CaptchaError("拼图验证未通过")
