"""项目归属鉴权。"""
from fastapi import Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import Project, Slide, User


async def get_owned_project(
    public_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    result = await db.execute(
        select(Project)
        .where(Project.public_id == public_id)
        .options(selectinload(Project.slides))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if project.user_id is None:
        raise HTTPException(status_code=403, detail="无权访问该项目")
    if project.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权访问该项目")
    return project


async def get_owned_slide(
    public_id: str,
    slide_id: int,
    project: Project = Depends(get_owned_project),
    db: AsyncSession = Depends(get_db),
) -> Slide:
    if project.public_id != public_id:
        raise HTTPException(status_code=404, detail="项目不存在")
    result = await db.execute(
        select(Slide).where(Slide.id == slide_id, Slide.project_id == project.id)
    )
    slide = result.scalar_one_or_none()
    if not slide:
        raise HTTPException(status_code=404, detail="页面不存在")
    return slide


async def resolve_owned_project_ref(
    ref: str,
    user: User,
    db: AsyncSession,
) -> Project:
    ref = (ref or "").strip()
    if not ref:
        raise HTTPException(status_code=404, detail="项目不存在")
    if ref.isdigit():
        result = await db.execute(
            select(Project).where(Project.id == int(ref)).options(selectinload(Project.slides))
        )
    else:
        result = await db.execute(
            select(Project)
            .where(or_(Project.public_id == ref, Project.share_slug == ref))
            .options(selectinload(Project.slides))
        )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if project.user_id is None or project.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权访问该项目")
    return project
