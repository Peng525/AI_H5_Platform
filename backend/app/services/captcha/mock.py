"""开发环境 mock 验证码（生产禁用）。"""
from app.services.captcha.base import CaptchaError, CaptchaProvider


class MockCaptchaProvider(CaptchaProvider):
    async def verify_ticket(self, ticket: str, randstr: str, user_ip: str) -> bool:
        if not ticket.strip() or not randstr.strip():
            raise CaptchaError("请完成拼图验证")
        return True
