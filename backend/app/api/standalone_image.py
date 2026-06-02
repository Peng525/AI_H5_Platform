"""独立 AI 生图（不绑定项目）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.schemas import GenerateImageRequest, GenerateImageResponse
from app.services.image_generator import generate_standalone_image
from app.services.llm.provider import LlmError

router = APIRouter(prefix="/api/v1", tags=["生图"])


@router.post("/生图/独立", response_model=GenerateImageResponse, summary="独立 AI 生图")
async def api_standalone_image(
    body: GenerateImageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await generate_standalone_image(db, body, user_id=user.id)
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return GenerateImageResponse(**result)
