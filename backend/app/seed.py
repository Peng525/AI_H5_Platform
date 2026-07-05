"""启动时可选写入种子用户与模板（凭证仅来自 .env，不进公开文档）。"""
from datetime import date

from sqlalchemy import select

from app.deps.security import pwd_context
from app.config import settings
from app.database import SessionLocal
from app.models import Order, Project, SiteVisitDaily, User
from app.services.h5_template_service import seed_default_templates
from app.services.image_prompt_template_service import seed_builtin_templates
from app.services.deck_prompt_template_service import seed_builtin_templates as seed_deck_builtin_templates


async def _ensure_user(db, username: str, password: str, tier: str = "free") -> None:
    if not username or not password:
        return
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
        await _ensure_user(
            db,
            settings.seed_demo_username.strip(),
            settings.seed_demo_password,
        )
        admin_user = settings.seed_admin_username.strip()
        if not admin_user and settings.admin_usernames.strip():
            admin_user = settings.admin_usernames.split(",")[0].strip()
        await _ensure_user(db, admin_user, settings.seed_admin_password)
        await seed_default_templates(db)
        await seed_builtin_templates(db)
        await seed_deck_builtin_templates(db)
        await _assign_orphan_projects(db)
        await db.commit()
        await _seed_demo_orders()


async def _assign_orphan_projects(db) -> None:
    seed_user = settings.seed_demo_username.strip()
    if not seed_user:
        return
    demo = await db.execute(select(User).where(User.username == seed_user))
    user = demo.scalar_one_or_none()
    if not user:
        return
    result = await db.execute(select(Project).where(Project.user_id.is_(None)))
    for project in result.scalars().all():
        project.user_id = user.id


async def _seed_demo_orders() -> None:
    seed_user = settings.seed_demo_username.strip()
    if not seed_user:
        return
    async with SessionLocal() as db:
        result = await db.execute(select(Order).limit(1))
        if result.scalar_one_or_none():
            return
        demo = await db.execute(select(User).where(User.username == seed_user))
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
