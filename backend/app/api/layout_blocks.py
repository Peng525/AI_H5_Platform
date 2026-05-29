"""编辑器素材版式 API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.schemas import LayoutBlockOut
from app.services.layout_block_service import LayoutBlockError, get_block, list_for_editor

router = APIRouter(prefix="/api/v1/版式", tags=["版式"])


@router.get("", response_model=list[LayoutBlockOut], summary="编辑器可用版式列表")
async def list_layout_blocks(
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await list_for_editor(db)
    return [LayoutBlockOut(**{**r, "enabled": bool(r.get("enabled"))}) for r in rows]


@router.get("/{block_id}", response_model=LayoutBlockOut, summary="版式详情")
async def get_layout_block(
    block_id: str,
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await get_block(db, block_id)
    if not row or not row.get("enabled"):
        raise HTTPException(status_code=404, detail="版式不存在")
    return LayoutBlockOut(**{**row, "enabled": bool(row.get("enabled"))})
