"""项目归属鉴权。"""
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import Project, Slide, User


async def get_owned_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id).options(selectinload(Project.slides))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if project.user_id is not None and project.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权访问该项目")
    return project


async def get_owned_slide(
    project_id: int,
    slide_id: int,
    project: Project = Depends(get_owned_project),
    db: AsyncSession = Depends(get_db),
) -> Slide:
    if project.id != project_id:
        raise HTTPException(status_code=404, detail="项目不存在")
    result = await db.execute(
        select(Slide).where(Slide.id == slide_id, Slide.project_id == project_id)
    )
    slide = result.scalar_one_or_none()
    if not slide:
        raise HTTPException(status_code=404, detail="页面不存在")
    return slide
