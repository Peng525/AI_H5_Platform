from app.services.payment.demo import DemoPaymentProvider
from app.services.payment.wechat_native import WechatNativePaymentProvider
from app.services.payment.wechat_qr import WechatQrPaymentProvider

PROVIDERS = {
    "demo": DemoPaymentProvider(),
    "wechat_qr": WechatQrPaymentProvider(),
    "wechat": WechatNativePaymentProvider(),
    "wechat_native": WechatNativePaymentProvider(),
}


def get_payment_provider(channel: str):
    provider = PROVIDERS.get(channel)
    if not provider:
        raise ValueError(f"不支持的支付渠道：{channel}")
    return provider
