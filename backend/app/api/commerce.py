"""访问统计与订单 API。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.schemas import OrderOut
from app.services.order_service import (
    LocalPaymentRequired,
    OrderServiceError,
    create_order,
    get_user_order,
    list_user_orders,
    order_snapshot,
)
from app.services.visits import record_visit

router = APIRouter(prefix="/api/v1", tags=["统计与订单"])


class OrderCreateRequest(BaseModel):
    plan_id: str = Field(..., description="newbie | sprint | monthly")
    payment_channel: str = Field("demo", description="wechat | alipay | demo")


class OrderCreateResponse(BaseModel):
    order_id: int
    plan_name: str
    amount: float
    status: str
    tier: str
    quota_remaining: int
    quota_total: int
    message: str
    qr_code_url: str | None = None


@router.post("/统计/访问", summary="记录站点访问")
async def track_visit(db: AsyncSession = Depends(get_db)):
    count = await record_visit(db)
    await db.commit()
    return {"ok": True, "today_count": count}


@router.post("/订单/创建", response_model=OrderCreateResponse, summary="创建支付订单")
async def api_create_order(
    body: OrderCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        order, message, qr_url = await create_order(db, user, body.plan_id, body.payment_channel)
        await db.commit()
        await db.refresh(user)
    except LocalPaymentRequired as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OrderServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    snap = order_snapshot(user)
    return OrderCreateResponse(
        order_id=order.id,
        plan_name=order.plan_name,
        amount=float(order.amount),
        status=order.status,
        tier=str(snap["tier"]),
        quota_remaining=int(snap["quota_remaining"]),
        quota_total=int(snap["quota_total"]),
        message=message,
        qr_code_url=qr_url,
    )


@router.get("/订单/{order_id}", response_model=OrderOut, summary="查询订单")
async def api_get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await get_user_order(db, user, order_id)
    except OrderServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return OrderOut(
        id=order.id,
        plan_id=order.plan_id,
        plan_name=order.plan_name,
        amount=float(order.amount),
        payment_channel=order.payment_channel,
        status=order.status,
        created_at=order.created_at,
    )


@router.get("/订单", response_model=list[OrderOut], summary="我的订单")
async def api_list_orders(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    orders = await list_user_orders(db, user)
    return [
        OrderOut(
            id=o.id,
            plan_id=o.plan_id,
            plan_name=o.plan_name,
            amount=float(o.amount),
            payment_channel=o.payment_channel,
            status=o.status,
            created_at=o.created_at,
        )
        for o in orders
    ]
