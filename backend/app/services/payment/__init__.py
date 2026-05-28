from app.services.payment.demo import DemoPaymentProvider

PROVIDERS = {
    "demo": DemoPaymentProvider(),
}


def get_payment_provider(channel: str) -> DemoPaymentProvider:
    provider = PROVIDERS.get(channel)
    if not provider:
        raise ValueError(f"不支持的支付渠道：{channel}")
    return provider
