"""H5 模板库 API。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.services.h5_template_service import CATEGORIES, DEVICES, get_template, list_for_user
from app.services.plan_pricing import (
    MONTHLY_QUOTA,
    PACK_QUOTA_MAX,
    PACK_QUOTA_MIN,
    monthly_price,
    pack_price,
    pricing_meta,
    resolve_plan,
)

router = APIRouter(prefix="/api/v1/模板库", tags=["模板库"])


@router.get("/分类", summary="模板分类")
async def categories(_user: User = Depends(get_current_user)):
    return {"items": CATEGORIES, "devices": DEVICES}


@router.get("", summary="探索模板列表")
async def list_templates(
    category: str = Query("全部"),
    device: str = Query("全部", description="全部 | mobile | web"),
    q: str = Query(""),
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await list_for_user(db, category, device, q)
    return {"items": items}


@router.get("/{template_id}/预览", summary="模板试看（含完整 slides 与 settings）")
async def preview_template(
    template_id: str,
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tpl = await get_template(db, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    return tpl


@router.get("/套餐/计价", summary="按次包实时计价")
async def quote_pack(
    quota: int = Query(20, ge=PACK_QUOTA_MIN, le=PACK_QUOTA_MAX),
    _user: User = Depends(get_current_user),
):
    spec = resolve_plan("custom", quota)
    return {
        "plan_id": "custom",
        "quota": spec.quota if spec else quota,
        "price": pack_price(quota),
        "name": spec.name if spec else f"AI 生图 {quota} 次",
    }


@router.get("/套餐", summary="升级套餐")
async def plans(_user: User = Depends(get_current_user)):
    monthly = resolve_plan("monthly")
    return {
        "pricing": pricing_meta(),
        "items": [
            {
                "id": "custom",
                "name": "按次生图包",
                "type": "custom",
                "quota_min": PACK_QUOTA_MIN,
                "quota_max": PACK_QUOTA_MAX,
                "quota_default": 20,
                "desc": "GPT 生图 · 10～50 次自选",
            },
            {
                "id": monthly.id if monthly else "monthly",
                "name": monthly.name if monthly else "官方直连包月",
                "type": "monthly",
                "price": monthly_price(),
                "quota": MONTHLY_QUOTA,
                "recommended": True,
                "desc": monthly.desc if monthly else f"每月 {MONTHLY_QUOTA} 次 · 尊享官方直连通道",
            },
        ],
    }
