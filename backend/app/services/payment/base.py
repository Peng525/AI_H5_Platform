"""支付渠道抽象。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models import Order, User


class PaymentError(Exception):
    pass


class PaymentNotConfigured(PaymentError):
    pass


@dataclass
class PaymentResult:
    status: str
    message: str
    qr_code_url: str | None = None


class PaymentProvider(ABC):
    channel: str

    @abstractmethod
    async def create_payment(self, order: Order, user: User) -> PaymentResult:
        raise NotImplementedError
