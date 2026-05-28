"""访问统计与订单 API。"""
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps.auth import get_current_user
from app.models import User
from app.schemas import OrderClaimRequest, OrderOut
from app.services.order_service import (
    LocalPaymentRequired,
    OrderServiceError,
    claim_order_paid,
    complete_wechat_native_payment,
    create_order,
    expire_stale_orders,
    get_user_order,
    list_user_orders,
    order_expires_at,
    order_snapshot,
)
from app.services.payment.wechat_native import decrypt_notify_resource, verify_notify_signature
from app.services.visits import record_visit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["统计与订单"])


class OrderCreateRequest(BaseModel):
    plan_id: str = Field(..., description="newbie | sprint | monthly")
    payment_channel: str = Field("demo", description="wechat | wechat_qr | demo")


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
    payment_channel: str = ""
    expires_at: Any | None = None


@router.get("/支付/微信收款码", summary="微信个人收款码地址")
async def wechat_qr_config():
    return {"qr_code_url": settings.wechat_personal_qr_url or "/static/wechat-pay-qr.png"}


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
    channel = body.payment_channel
    if channel == "wechat":
        channel = "wechat_native"
    try:
        order, message, qr_url = await create_order(db, user, body.plan_id, channel)
        await db.commit()
        await db.refresh(user)
    except LocalPaymentRequired as exc:
        status_code = 503 if channel in ("wechat_native", "wechat") else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
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
        payment_channel=order.payment_channel,
        expires_at=order_expires_at(order) if order.status in ("pending", "claimed") else None,
    )


@router.post("/支付/回调/wechat", summary="微信支付异步通知")
async def wechat_pay_notify(request: Request, db: AsyncSession = Depends(get_db)):
    body_bytes = await request.body()
    timestamp = request.headers.get("Wechatpay-Timestamp", "")
    nonce = request.headers.get("Wechatpay-Nonce", "")
    signature = request.headers.get("Wechatpay-Signature", "")
    serial = request.headers.get("Wechatpay-Serial", "")

    if not verify_notify_signature(timestamp, nonce, body_bytes, signature, serial):
        logger.warning("WeChat notify signature rejected")
        return JSONResponse({"code": "FAIL", "message": "签名失败"}, status_code=401)

    try:
        envelope = json.loads(body_bytes.decode("utf-8"))
        resource = envelope.get("resource") or {}
        plain = decrypt_notify_resource(resource)
    except Exception:
        logger.exception("WeChat notify decrypt failed")
        return JSONResponse({"code": "FAIL", "message": "解密失败"}, status_code=400)

    trade_state = plain.get("trade_state")
    out_trade_no = plain.get("out_trade_no", "")
    transaction_id = plain.get("transaction_id", "")

    if trade_state == "SUCCESS" and out_trade_no:
        try:
            await complete_wechat_native_payment(
                db,
                out_trade_no,
                transaction_id,
                body_bytes.decode("utf-8", errors="replace"),
            )
            await db.commit()
        except OrderServiceError:
            await db.rollback()
            logger.exception("WeChat notify order update failed")

    return JSONResponse({"code": "SUCCESS", "message": "成功"})


@router.post("/订单/{order_id}/申报已付", response_model=OrderOut, summary="用户申报已完成微信转账")
async def api_claim_order(
    order_id: int,
    body: OrderClaimRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await claim_order_paid(db, user, order_id, body.remark)
        await db.commit()
    except OrderServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _order_out(order)


@router.get("/订单/{order_id}", response_model=OrderOut, summary="查询订单")
async def api_get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await get_user_order(db, user, order_id)
        await db.commit()
    except OrderServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _order_out(order)


@router.get("/订单", response_model=list[OrderOut], summary="我的订单")
async def api_list_orders(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    orders = await list_user_orders(db, user)
    return [_order_out(o) for o in orders]


def _order_out(order) -> OrderOut:
    expires = order_expires_at(order) if order.status in ("pending", "claimed") else None
    return OrderOut(
        id=order.id,
        plan_id=order.plan_id,
        plan_name=order.plan_name,
        amount=float(order.amount),
        payment_channel=order.payment_channel,
        status=order.status,
        user_remark=getattr(order, "user_remark", "") or "",
        admin_remark=getattr(order, "admin_remark", "") or "",
        created_at=order.created_at,
        claimed_at=getattr(order, "claimed_at", None),
        confirmed_at=getattr(order, "confirmed_at", None),
        expires_at=expires,
    )
