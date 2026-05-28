"""微信个人收款码：创建待支付订单，由管理员人工确认。"""
from app.config import settings
from app.models import Order, User
from app.services.payment.base import PaymentProvider, PaymentResult


class WechatQrPaymentProvider(PaymentProvider):
    channel = "wechat_qr"

    async def create_payment(self, order: Order, user: User) -> PaymentResult:
        qr_url = settings.wechat_personal_qr_url.strip() or "/static/wechat-pay-qr.png"
        return PaymentResult(
            status="pending",
            message=f"请微信扫码支付 ¥{float(order.amount):.2f}，支付后点击「我已支付」",
            qr_code_url=qr_url,
        )
