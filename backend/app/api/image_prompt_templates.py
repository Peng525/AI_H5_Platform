"""编辑器 AI 生图提示词模板 API。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.schemas import ImagePromptTemplatePublicOut
from app.services.image_prompt_template_service import list_for_editor

router = APIRouter(prefix="/api/v1/生图提示词", tags=["生图提示词"])


@router.get("", response_model=list[ImagePromptTemplatePublicOut], summary="编辑器可用生图提示词模板")
async def list_image_prompt_templates(
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await list_for_editor(db)
    return [ImagePromptTemplatePublicOut(**r) for r in rows]
