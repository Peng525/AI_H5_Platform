"""启动时写入演示账号。"""
from datetime import date

from sqlalchemy import select

from app.api.auth import pwd_context
from app.database import SessionLocal
from app.models import Order, Project, SiteVisitDaily, User
from app.services.h5_template_service import seed_default_templates

DEMO_ACCOUNT = "demo@ai-h5.com"
DEMO_PASSWORD = "demo123456"
ADMIN_ACCOUNT = "admin@ai-h5.com"
ADMIN_PASSWORD = "admin123456"


async def _ensure_user(db, username: str, password: str, tier: str = "free") -> None:
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        return
    db.add(
        User(
            username=username,
            password_hash=pwd_context.hash(password),
            tier=tier,
            free_quota_used=0,
        )
    )


async def seed_demo_user() -> None:
    async with SessionLocal() as db:
        await _ensure_user(db, DEMO_ACCOUNT, DEMO_PASSWORD)
        await _ensure_user(db, ADMIN_ACCOUNT, ADMIN_PASSWORD)
        await seed_default_templates(db)
        await _assign_orphan_projects(db)
        await db.commit()
        await _seed_demo_orders()


async def _assign_orphan_projects(db) -> None:
    demo = await db.execute(select(User).where(User.username == DEMO_ACCOUNT))
    user = demo.scalar_one_or_none()
    if not user:
        return
    result = await db.execute(select(Project).where(Project.user_id.is_(None)))
    for project in result.scalars().all():
        project.user_id = user.id


async def _seed_demo_orders() -> None:
    async with SessionLocal() as db:
        result = await db.execute(select(Order).limit(1))
        if result.scalar_one_or_none():
            return
        demo = await db.execute(select(User).where(User.username == DEMO_ACCOUNT))
        user = demo.scalar_one_or_none()
        if user:
            db.add(
                Order(
                    user_id=user.id,
                    plan_id="monthly",
                    plan_name="毕业专属包月",
                    amount=29.9,
                    payment_channel="demo",
                    status="paid",
                )
            )
        today = date.today()
        visit = await db.execute(select(SiteVisitDaily).where(SiteVisitDaily.visit_date == today))
        if not visit.scalar_one_or_none():
            db.add(SiteVisitDaily(visit_date=today, count=12))
        await db.commit()
