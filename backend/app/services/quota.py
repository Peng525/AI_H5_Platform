"""AI 配额校验。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import User


class QuotaExceeded(Exception):
    pass


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
    if user.free_quota_used >= settings.free_quota_per_user:
        raise QuotaExceeded(f"免费 AI 次数已用完（{settings.free_quota_per_user} 次），请升级套餐")
    user.free_quota_used += 1
    await db.flush()
