"""腾讯云验证码 ticket 服务端校验。"""
import httpx

from app.config import settings
from app.services.captcha.base import CaptchaError, CaptchaProvider


class TencentCaptchaProvider(CaptchaProvider):
    async def verify_ticket(self, ticket: str, randstr: str, user_ip: str) -> bool:
        app_id = settings.tencent_captcha_app_id.strip()
        secret = settings.tencent_captcha_app_secret_key.strip()
        if not app_id or not secret:
            raise CaptchaError("验证码服务未配置")

        params = {
            "aid": app_id,
            "AppSecretKey": secret,
            "Ticket": ticket.strip(),
            "Randstr": randstr.strip(),
            "UserIP": user_ip or "127.0.0.1",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get("https://ssl.captcha.qq.com/ticket/verify", params=params)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise CaptchaError("验证码服务暂时不可用") from exc

        if str(data.get("response")) == "1":
            return True
        raise CaptchaError("拼图验证未通过，请重试")
