"""H5 模板库 API。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.services.h5_template_service import CATEGORIES, DEVICES, list_for_user

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


@router.get("/套餐", summary="升级套餐")
async def plans(_user: User = Depends(get_current_user)):
    return {
        "items": [
            {"id": "newbie", "name": "新手包", "price": 9.9, "quota": 50, "desc": "50 次官方高速调用"},
            {"id": "sprint", "name": "毕业冲刺包", "price": 19.9, "quota": 100, "desc": "100 次 + 高级模板"},
            {
                "id": "monthly",
                "name": "毕业专属包月",
                "price": 29.9,
                "quota": -1,
                "recommended": True,
                "desc": "无限次官方直连",
            },
        ]
    }
