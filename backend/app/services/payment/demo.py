"""演示支付：本地直付成功。"""
from app.models import Order, User
from app.services.payment.base import PaymentProvider, PaymentResult


class DemoPaymentProvider(PaymentProvider):
    channel = "demo"

    async def create_payment(self, order: Order, user: User) -> PaymentResult:
        return PaymentResult(
            status="paid",
            message=f"演示支付成功，已开通「{order.plan_name}」",
        )
