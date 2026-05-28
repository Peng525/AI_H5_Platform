"""订单创建与查询。"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import Order, User
from app.services.payment import get_payment_provider
from app.services.payment.url_utils import wechat_qr_path
from app.services.payment.base import PaymentError, PaymentNotConfigured
from app.services.quota import apply_plan_to_user, get_plan, quota_remaining, quota_total


class OrderServiceError(Exception):
    pass


class LocalPaymentRequired(OrderServiceError):
    """本地部署不支持该扫码渠道。"""


WECHAT_CHANNELS = frozenset({"wechat", "wechat_qr", "wechat_native"})
ADMIN_CONFIRM_STATUSES = frozenset({"pending", "claimed"})
EXPIRABLE_STATUSES = frozenset({"pending", "claimed"})


def _is_wechat_order(order: Order) -> bool:
    return order.payment_channel in WECHAT_CHANNELS


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def order_expires_at(order: Order) -> datetime:
    return _as_utc(order.created_at) + timedelta(minutes=settings.order_pending_expire_minutes)


def is_order_expired(order: Order) -> bool:
    if order.status not in EXPIRABLE_STATUSES:
        return False
    return datetime.now(timezone.utc) >= order_expires_at(order)


def seconds_until_order_expires(order: Order) -> int:
    remaining = (order_expires_at(order) - datetime.now(timezone.utc)).total_seconds()
    return max(0, int(remaining))


def _qr_url_for_order(order: Order) -> str | None:
    if order.code_url:
        return order.code_url
    if order.payment_channel in ("wechat", "wechat_qr"):
        return wechat_qr_path()
    return None


async def expire_stale_orders(db: AsyncSession, user_id: int | None = None) -> int:
    """将超时未支付的订单标记为 expired。"""
    query = select(Order).where(Order.status.in_(tuple(EXPIRABLE_STATUSES)))
    if user_id is not None:
        query = query.where(Order.user_id == user_id)
    result = await db.execute(query)
    expired_count = 0
    for order in result.scalars().all():
        if is_order_expired(order):
            order.status = "expired"
            order.admin_remark = (order.admin_remark or "超时未支付，订单已关闭")[:255]
            expired_count += 1
    if expired_count:
        await db.flush()
    return expired_count


async def _find_reusable_pending_order(
    db: AsyncSession,
    user: User,
    plan_id: str,
    payment_channel: str,
    quota: int | None = None,
) -> Order | None:
    query = (
        select(Order)
        .where(
            Order.user_id == user.id,
            Order.plan_id == plan_id,
            Order.payment_channel == payment_channel,
            Order.status.in_(tuple(EXPIRABLE_STATUSES)),
        )
        .order_by(Order.created_at.desc())
        .limit(1)
    )
    if plan_id == "custom" and quota is not None:
        query = query.where(Order.plan_quota == quota)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    if order and not is_order_expired(order):
        return order
    return None


async def create_order(
    db: AsyncSession,
    user: User,
    plan_id: str,
    payment_channel: str,
    quota: int | None = None,
) -> tuple[Order, str, str | None]:
    if plan_id == "custom" and quota is None:
        raise OrderServiceError("请指定生图次数（10～50）")
    plan = get_plan(plan_id, quota)
    if not plan:
        raise OrderServiceError("未知套餐")

    if payment_channel == "alipay":
        raise LocalPaymentRequired("本地部署暂不支持支付宝，请使用微信收款码或演示支付")

    if payment_channel in WECHAT_CHANNELS:
        await expire_stale_orders(db, user.id)
        existing = await _find_reusable_pending_order(db, user, plan_id, payment_channel, quota)
        if existing:
            msg = (
                f"请使用微信扫码支付 ¥{float(existing.amount):.2f}，"
                f"请在 {settings.order_pending_expire_minutes} 分钟内完成转账"
            )
            return existing, msg, _qr_url_for_order(existing)

    try:
        provider = get_payment_provider(payment_channel)
    except ValueError as exc:
        raise OrderServiceError(str(exc)) from exc

    order_quota = plan["quota"] if plan_id in ("custom", "monthly") else None
    order = Order(
        user_id=user.id,
        plan_id=plan_id,
        plan_name=plan["name"],
        amount=plan["price"],
        payment_channel=payment_channel,
        status="pending",
        plan_quota=order_quota,
    )
    db.add(order)
    await db.flush()

    try:
        result = await provider.create_payment(order, user)
    except PaymentNotConfigured as exc:
        order.status = "failed"
        await db.flush()
        raise LocalPaymentRequired(str(exc)) from exc
    except PaymentError as exc:
        order.status = "failed"
        await db.flush()
        raise OrderServiceError(str(exc)) from exc

    order.status = result.status
    if result.status == "paid":
        apply_plan_to_user(user, plan_id, quota)

    await db.flush()
    message = result.message
    if order.status in EXPIRABLE_STATUSES:
        message = (
            f"请使用微信扫码支付 ¥{float(order.amount):.2f}，"
            f"请在 {settings.order_pending_expire_minutes} 分钟内完成转账"
        )
    return order, message, result.qr_code_url


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
    await expire_stale_orders(db, order.user_id)
    await db.refresh(order)
    if order.status == "expired":
        raise OrderServiceError("订单已超时关闭，请让用户重新下单")
    if order.status not in ADMIN_CONFIRM_STATUSES:
        raise OrderServiceError("该订单状态不可确认收款")
    if not _is_wechat_order(order):
        raise OrderServiceError("仅微信收款码订单支持人工确认")
    user = await db.get(User, order.user_id)
    if not user:
        raise OrderServiceError("订单用户不存在")
    order.status = "paid"
    order.admin_remark = (admin_remark or "").strip()[:255]
    order.confirmed_at = datetime.now(timezone.utc)
    apply_plan_to_user(user, order.plan_id, order.plan_quota)
    await db.flush()
    return order


async def reject_order_payment(
    db: AsyncSession,
    order: Order,
    admin_remark: str = "",
) -> Order:
    if order.status not in ADMIN_CONFIRM_STATUSES:
        raise OrderServiceError("该订单状态不可拒绝")
    if not _is_wechat_order(order):
        raise OrderServiceError("仅微信收款码订单支持人工拒绝")
    order.status = "rejected"
    order.admin_remark = (admin_remark or "未收到款项")[:255]
    await db.flush()
    return order


async def get_order_by_out_trade_no(db: AsyncSession, out_trade_no: str) -> Order | None:
    result = await db.execute(select(Order).where(Order.out_trade_no == out_trade_no))
    return result.scalar_one_or_none()


async def complete_wechat_native_payment(
    db: AsyncSession,
    out_trade_no: str,
    transaction_id: str,
    notify_raw: str,
) -> Order | None:
    """微信支付回调幂等开通套餐。"""
    order = await get_order_by_out_trade_no(db, out_trade_no)
    if not order:
        return None
    if order.status == "paid":
        return order
    if order.payment_channel not in ("wechat", "wechat_native"):
        return order

    if transaction_id and order.transaction_id == transaction_id:
        return order

    user = await db.get(User, order.user_id)
    if not user:
        raise OrderServiceError("订单用户不存在")

    order.status = "paid"
    order.transaction_id = transaction_id
    order.paid_at = datetime.now(timezone.utc)
    order.notify_raw = notify_raw[:8000] if notify_raw else None
    order.confirmed_at = order.paid_at
    apply_plan_to_user(user, order.plan_id, order.plan_quota)
    await db.flush()
    return order


async def get_user_order(db: AsyncSession, user: User, order_id: int) -> Order:
    order = await get_order_by_id(db, order_id)
    if not order or order.user_id != user.id:
        raise OrderServiceError("订单不存在")
    if order.status in EXPIRABLE_STATUSES and is_order_expired(order):
        order.status = "expired"
        order.admin_remark = (order.admin_remark or "超时未支付，订单已关闭")[:255]
        await db.flush()
    return order


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | None:
    return await db.get(Order, order_id)


async def list_user_orders(db: AsyncSession, user: User, limit: int = 20) -> list[Order]:
    result = await db.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def list_pending_wechat_orders(db: AsyncSession, limit: int = 50) -> list[Order]:
    """待管理员确认的微信个人收款码订单（含 pending 与 claimed，已排除超时）。"""
    await expire_stale_orders(db)
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.user))
        .where(
            Order.status.in_(tuple(ADMIN_CONFIRM_STATUSES)),
            Order.payment_channel.in_(tuple(WECHAT_CHANNELS)),
        )
        .order_by(Order.created_at.desc())
        .limit(limit)
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
