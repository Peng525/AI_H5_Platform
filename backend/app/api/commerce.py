"""访问统计与订单 API。"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.services.quota import create_paid_order, quota_remaining, quota_total
from app.services.visits import record_visit

router = APIRouter(prefix="/api/v1", tags=["统计与订单"])


class OrderCreateRequest(BaseModel):
    plan_id: str = Field(..., description="newbie | sprint | monthly")
    payment_channel: str = Field("demo", description="wechat | alipay | demo")


class OrderCreateResponse(BaseModel):
    order_id: int
    plan_name: str
    amount: float
    tier: str
    quota_remaining: int
    quota_total: int
    message: str


@router.post("/统计/访问", summary="记录站点访问")
async def track_visit(db: AsyncSession = Depends(get_db)):
    count = await record_visit(db)
    await db.commit()
    return {"ok": True, "today_count": count}


@router.post("/订单/创建", response_model=OrderCreateResponse, summary="创建支付订单")
async def create_order(
    body: OrderCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await create_paid_order(db, user, body.plan_id, body.payment_channel)
        await db.commit()
        await db.refresh(user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return OrderCreateResponse(
        order_id=order.id,
        plan_name=order.plan_name,
        amount=float(order.amount),
        tier=user.tier,
        quota_remaining=quota_remaining(user),
        quota_total=quota_total(user),
        message=f"订单已支付，已开通「{order.plan_name}」",
    )
