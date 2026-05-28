"""用户配额与订单权益。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Order, User


class QuotaExceeded(Exception):
    pass


def quota_total(user: User) -> int:
    if user.tier == "pro":
        return 9999
    if user.quota_limit is not None:
        return user.quota_limit
    return settings.free_quota_per_user


def quota_remaining(user: User) -> int:
    if user.tier == "pro":
        return 9999
    return max(0, quota_total(user) - user.free_quota_used)


async def check_and_consume(db: AsyncSession, user_id: int | None, tier: str) -> None:
    if tier == "pro":
        return
    if not user_id:
        return
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return
    if user.tier == "pro":
        return
    total = quota_total(user)
    if user.free_quota_used >= total:
        raise QuotaExceeded(f"免费 AI 次数已用完（{total} 次），请升级套餐")
    user.free_quota_used += 1
    await db.flush()


PLAN_CATALOG = {
    "newbie": {"name": "新手包", "price": 9.9, "quota": 50, "tier": "free"},
    "sprint": {"name": "毕业冲刺包", "price": 19.9, "quota": 100, "tier": "free"},
    "monthly": {"name": "毕业专属包月", "price": 29.9, "quota": -1, "tier": "pro"},
}


def apply_plan_to_user(user: User, plan_id: str) -> None:
    plan = PLAN_CATALOG.get(plan_id)
    if not plan:
        return
    if plan["tier"] == "pro":
        user.tier = "pro"
    else:
        user.tier = "free"
        user.quota_limit = plan["quota"]
        user.free_quota_used = 0


async def create_paid_order(
    db: AsyncSession,
    user: User,
    plan_id: str,
    payment_channel: str = "demo",
) -> Order:
    plan = PLAN_CATALOG.get(plan_id)
    if not plan:
        raise ValueError("未知套餐")
    order = Order(
        user_id=user.id,
        plan_id=plan_id,
        plan_name=plan["name"],
        amount=plan["price"],
        payment_channel=payment_channel,
        status="paid",
    )
    db.add(order)
    apply_plan_to_user(user, plan_id)
    await db.flush()
    return order
