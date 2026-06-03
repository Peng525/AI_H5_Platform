"""公开：演示文稿提示词模板列表。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.schemas import DeckPromptTemplatePublicOut
from app.services.deck_prompt_template_service import list_for_editor

router = APIRouter(prefix="/api/v1/演示提示词", tags=["演示提示词"])


@router.get("", response_model=list[DeckPromptTemplatePublicOut], summary="生成页可用演示提示词模板")
async def list_deck_prompt_templates(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows = await list_for_editor(db)
    return [DeckPromptTemplatePublicOut(**r) for r in rows]
