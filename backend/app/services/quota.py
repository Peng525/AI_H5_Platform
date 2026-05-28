"""用户配额与订单权益。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Order, User
from app.services.plan_pricing import resolve_plan


class QuotaExceeded(Exception):
    pass


def quota_total(user: User) -> int:
    if user.quota_limit is not None:
        return user.quota_limit
    if user.tier == "pro":
        return 9999
    return settings.free_quota_per_user


def quota_remaining(user: User) -> int:
    if user.tier == "pro" and user.quota_limit is None:
        return 9999
    return max(0, quota_total(user) - user.free_quota_used)


async def check_and_consume(db: AsyncSession, user_id: int | None, tier: str) -> None:
    if not user_id:
        return
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return
    if user.tier == "pro" and user.quota_limit is None:
        return
    total = quota_total(user)
    if user.free_quota_used >= total:
        raise QuotaExceeded(f"AI 配图次数已用完（{total} 次），请升级套餐")
    user.free_quota_used += 1
    await db.flush()


# 兼容旧订单 plan_id
LEGACY_PLANS = {
    "newbie": {"name": "新手包", "price": 9.9, "quota": 50, "tier": "free", "desc": ""},
    "sprint": {"name": "毕业冲刺包", "price": 19.9, "quota": 100, "tier": "free", "desc": ""},
}

PLAN_CATALOG = {
    "custom": {"name": "按次配图包", "price": 0, "quota": 0, "tier": "free", "desc": ""},
    "monthly": {"name": "官方直连包月", "price": 30.0, "quota": 60, "tier": "pro", "desc": ""},
}


def get_plan(plan_id: str, quota: int | None = None):
    spec = resolve_plan(plan_id, quota)
    if spec:
        return {
            "id": spec.id,
            "name": spec.name,
            "price": spec.price,
            "quota": spec.quota,
            "tier": spec.tier,
            "desc": spec.desc,
        }
    legacy = LEGACY_PLANS.get(plan_id)
    if legacy:
        return dict(legacy)
    static = PLAN_CATALOG.get(plan_id)
    if static:
        return dict(static)
    return None


def apply_plan_to_user(user: User, plan_id: str, quota: int | None = None) -> None:
    plan = get_plan(plan_id, quota)
    if not plan:
        return
    user.tier = plan["tier"]
    q = plan.get("quota", 0)
    if q > 0:
        user.quota_limit = q
        user.free_quota_used = 0
    elif plan["tier"] == "pro":
        user.quota_limit = None


async def create_paid_order(
    db: AsyncSession,
    user: User,
    plan_id: str,
    payment_channel: str = "demo",
    quota: int | None = None,
) -> Order:
    plan = get_plan(plan_id, quota)
    if not plan:
        raise ValueError("未知套餐")
    order = Order(
        user_id=user.id,
        plan_id=plan_id,
        plan_name=plan["name"],
        amount=plan["price"],
        payment_channel=payment_channel,
        status="paid",
        plan_quota=plan["quota"] if plan_id == "custom" else (plan["quota"] if plan_id == "monthly" else None),
    )
    db.add(order)
    apply_plan_to_user(user, plan_id, quota)
    await db.flush()
    return order
