"""启动时写入演示账号。"""
from sqlalchemy import select

from app.api.auth import pwd_context
from app.database import SessionLocal
from app.models import User

DEMO_ACCOUNT = "demo@ai-h5.com"
DEMO_PASSWORD = "demo123456"


async def seed_demo_user() -> None:
    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.username == DEMO_ACCOUNT))
        if result.scalar_one_or_none():
            return
        db.add(
            User(
                username=DEMO_ACCOUNT,
                password_hash=pwd_context.hash(DEMO_PASSWORD),
                tier="free",
                free_quota_used=0,
            )
        )
        await db.commit()
