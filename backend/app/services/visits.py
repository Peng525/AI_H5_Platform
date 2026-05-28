"""站点访问统计。"""
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SiteVisitDaily


async def record_visit(db: AsyncSession) -> int:
    today = date.today()
    result = await db.execute(select(SiteVisitDaily).where(SiteVisitDaily.visit_date == today))
    row = result.scalar_one_or_none()
    if row:
        row.count += 1
    else:
        row = SiteVisitDaily(visit_date=today, count=1)
        db.add(row)
    await db.flush()
    return row.count


async def visit_stats(db: AsyncSession, days: int = 30) -> dict:
    since = date.today() - timedelta(days=days - 1)
    result = await db.execute(
        select(SiteVisitDaily).where(SiteVisitDaily.visit_date >= since).order_by(SiteVisitDaily.visit_date)
    )
    rows = result.scalars().all()
    by_date = {r.visit_date: r.count for r in rows}
    chart = []
    for i in range(days):
        d = since + timedelta(days=i)
        chart.append({"date": d.isoformat(), "count": by_date.get(d, 0)})
    today = date.today()
    week_ago = today - timedelta(days=6)
    month_ago = today - timedelta(days=29)
    visits_today = by_date.get(today, 0)
    visits_7d = sum(c for d, c in by_date.items() if d >= week_ago)
    visits_30d = sum(c for d, c in by_date.items() if d >= month_ago)
    return {
        "visits_today": visits_today,
        "visits_7d": visits_7d,
        "visits_30d": visits_30d,
        "chart": chart,
    }
