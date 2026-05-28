"""订单创建与查询。"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, User
from app.services.payment import get_payment_provider
from app.services.payment.base import PaymentError
from app.services.quota import PLAN_CATALOG, apply_plan_to_user, quota_remaining, quota_total


class OrderServiceError(Exception):
    pass


class LocalPaymentRequired(OrderServiceError):
    """本地部署不支持该扫码渠道。"""


async def create_order(
    db: AsyncSession,
    user: User,
    plan_id: str,
    payment_channel: str,
) -> tuple[Order, str, str | None]:
    plan = PLAN_CATALOG.get(plan_id)
    if not plan:
        raise OrderServiceError("未知套餐")

    if payment_channel == "alipay":
        raise LocalPaymentRequired("本地部署暂不支持支付宝，请使用微信收款码或演示支付")

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


async def claim_order_paid(
    db: AsyncSession,
    user: User,
    order_id: int,
    remark: str = "",
) -> Order:
    order = await get_user_order(db, user, order_id)
    if order.status not in ("pending", "claimed"):
        raise OrderServiceError("该订单状态不可申报")
    order.status = "claimed"
    order.user_remark = (remark or "").strip()[:255]
    order.claimed_at = datetime.now(timezone.utc)
    await db.flush()
    return order


async def confirm_order_payment(
    db: AsyncSession,
    order: Order,
    admin_remark: str = "",
) -> Order:
    if order.status != "claimed":
        raise OrderServiceError("仅「待确认」订单可确认收款")
    user = await db.get(User, order.user_id)
    if not user:
        raise OrderServiceError("订单用户不存在")
    order.status = "paid"
    order.admin_remark = (admin_remark or "").strip()[:255]
    order.confirmed_at = datetime.now(timezone.utc)
    apply_plan_to_user(user, order.plan_id)
    await db.flush()
    return order


async def reject_order_payment(
    db: AsyncSession,
    order: Order,
    admin_remark: str = "",
) -> Order:
    if order.status != "claimed":
        raise OrderServiceError("仅「待确认」订单可拒绝")
    order.status = "rejected"
    order.admin_remark = (admin_remark or "未收到款项")[:255]
    await db.flush()
    return order


async def get_user_order(db: AsyncSession, user: User, order_id: int) -> Order:
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise OrderServiceError("订单不存在")
    return order


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | None:
    return await db.get(Order, order_id)


async def list_user_orders(db: AsyncSession, user: User, limit: int = 20) -> list[Order]:
    result = await db.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def list_claimed_orders(db: AsyncSession, limit: int = 50) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.status == "claimed")
        .order_by(Order.claimed_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


def order_snapshot(user: User) -> dict[str, int | str]:
    return {
        "tier": user.tier,
        "quota_remaining": quota_remaining(user),
        "quota_total": quota_total(user),
    }
