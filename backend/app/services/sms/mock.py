"""开发环境 mock 短信。"""
import logging

from app.services.sms.base import SmsProvider

logger = logging.getLogger(__name__)


class MockSmsProvider(SmsProvider):
    async def send_code(self, phone: str, code: str) -> None:
        logger.info("mock SMS to %s (code omitted in production logs)", phone[:3] + "****" + phone[-4:])
