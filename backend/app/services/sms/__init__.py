from app.config import settings
from app.services.sms.base import SmsError, SmsProvider
from app.services.sms.mock import MockSmsProvider
from app.services.sms.tencent_sms import TencentSmsProvider

_PROVIDERS: dict[str, SmsProvider] = {
    "mock": MockSmsProvider(),
    "tencent": TencentSmsProvider(),
}


def get_sms_provider() -> SmsProvider:
    name = (settings.sms_provider or "mock").strip().lower()
    provider = _PROVIDERS.get(name)
    if not provider:
        raise SmsError(f"未知短信提供商：{name}")
    return provider
