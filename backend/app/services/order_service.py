"""订单创建与查询。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, User
from app.services.payment import get_payment_provider
from app.services.payment.base import PaymentError
from app.services.quota import PLAN_CATALOG, apply_plan_to_user, quota_remaining, quota_total


class OrderServiceError(Exception):
    pass


class LocalPaymentRequired(OrderServiceError):
    """本地部署不支持真实扫码渠道。"""


async def create_order(
    db: AsyncSession,
    user: User,
    plan_id: str,
    payment_channel: str,
) -> tuple[Order, str, str | None]:
    plan = PLAN_CATALOG.get(plan_id)
    if not plan:
        raise OrderServiceError("未知套餐")

    if payment_channel in ("wechat", "alipay"):
        raise LocalPaymentRequired("本地部署请使用「演示：模拟支付成功」")

    try:
        provider = get_payment_provider(payment_channel)
    except ValueError as exc:
        raise OrderServiceError(str(exc)) from exc

    order = Order(
        user_id=user.id,
        plan_id=plan_id,
        plan_name=plan["name"],
        amount=plan["price"],
        payment_channel=payment_channel,
        status="pending",
    )
    db.add(order)
    await db.flush()

    try:
        result = await provider.create_payment(order, user)
    except PaymentError as exc:
        order.status = "failed"
        await db.flush()
        raise OrderServiceError(str(exc)) from exc

    order.status = result.status
    if result.status == "paid":
        apply_plan_to_user(user, plan_id)

    await db.flush()
    return order, result.message, result.qr_code_url


async def get_user_order(db: AsyncSession, user: User, order_id: int) -> Order:
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise OrderServiceError("订单不存在")
    return order


async def list_user_orders(db: AsyncSession, user: User, limit: int = 20) -> list[Order]:
    result = await db.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


def order_snapshot(user: User) -> dict[str, int | str]:
    return {
        "tier": user.tier,
        "quota_remaining": quota_remaining(user),
        "quota_total": quota_total(user),
    }
