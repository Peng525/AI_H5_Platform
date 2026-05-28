"""管理员 API。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import pwd_context
from app.database import get_db
from app.deps.auth import require_admin
from app.models import Order, User
from app.schemas import H5TemplateCreate, H5TemplateOut, H5TemplateUpdate, RelayQuotaOut
from app.services.h5_template_service import (
    H5TemplateError,
    admin_list,
    create_template,
    delete_template,
    update_template,
)
from app.services.order_service import (
    OrderServiceError,
    confirm_order_payment,
    get_order_by_id,
    list_pending_wechat_orders,
    reject_order_payment,
)
from app.services.quota import quota_remaining, quota_total
from app.services.relay_quota_service import RelayQuotaError, fetch_relay_quota
from app.services.visits import visit_stats

router = APIRouter(prefix="/api/v1/管理", tags=["管理"])


class AdminUserOut(BaseModel):
    id: int
    username: str
    tier: str
    quota_used: int
    quota_total: int
    quota_remaining: int
    created_at: datetime | None = None


class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6)
    tier: str = Field("free", description="free | pro")
    quota_limit: int | None = Field(None, description="免费档配额上限，留空用系统默认")


class AdminUserUpdate(BaseModel):
    tier: str | None = None
    quota_limit: int | None = None
    free_quota_used: int | None = Field(None, ge=0)
    password: str | None = Field(None, min_length=6)


class AdminOrderOut(BaseModel):
    id: int
    user_id: int
    username: str
    plan_id: str
    plan_name: str
    amount: float
    payment_channel: str
    status: str
    user_remark: str = ""
    admin_remark: str = ""
    quota_remaining: int
    created_at: datetime | None = None
    claimed_at: datetime | None = None


class AdminDashboardOut(BaseModel):
    visits_today: int
    visits_7d: int
    visits_30d: int
    orders_total: int
    orders_paid: int
    orders_pending_confirm: int
    revenue_total: float
    users_total: int
    visit_chart: list[dict]
    recent_orders: list[AdminOrderOut]
    pending_payment_orders: list[AdminOrderOut]


def _user_out(user: User) -> AdminUserOut:
    total = quota_total(user)
    return AdminUserOut(
        id=user.id,
        username=user.username,
        tier=user.tier,
        quota_used=user.free_quota_used,
        quota_total=total,
        quota_remaining=quota_remaining(user),
        created_at=user.created_at,
    )


def _order_out(order: Order, user: User | None = None) -> AdminOrderOut:
    u = user or order.user
    return AdminOrderOut(
        id=order.id,
        user_id=order.user_id,
        username=u.username if u else "",
        plan_id=order.plan_id,
        plan_name=order.plan_name,
        amount=float(order.amount),
        payment_channel=order.payment_channel,
        status=order.status,
        user_remark=getattr(order, "user_remark", "") or "",
        admin_remark=getattr(order, "admin_remark", "") or "",
        quota_remaining=quota_remaining(u) if u else 0,
        created_at=order.created_at,
        claimed_at=getattr(order, "claimed_at", None),
    )


@router.get("/仪表盘", response_model=AdminDashboardOut, summary="管理员仪表盘")
async def admin_dashboard(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    stats = await visit_stats(db, days=14)
    orders_total = await db.scalar(select(func.count(Order.id))) or 0
    orders_paid = await db.scalar(select(func.count(Order.id)).where(Order.status == "paid")) or 0
    revenue = await db.scalar(
        select(func.coalesce(func.sum(Order.amount), 0)).where(Order.status == "paid")
    )
    users_total = await db.scalar(select(func.count(User.id))) or 0

    result = await db.execute(
        select(Order)
        .options(selectinload(Order.user))
        .order_by(Order.created_at.desc())
        .limit(20)
    )
    recent = [_order_out(o) for o in result.scalars().all()]

    pending_result = await db.execute(
        select(Order)
        .options(selectinload(Order.user))
        .where(
            Order.status.in_(("pending", "claimed")),
            Order.payment_channel.in_(("wechat", "wechat_qr")),
        )
        .order_by(Order.created_at.desc())
        .limit(10)
    )
    pending_orders = [_order_out(o) for o in pending_result.scalars().all()]
    orders_pending = await db.scalar(
        select(func.count(Order.id)).where(
            Order.status.in_(("pending", "claimed")),
            Order.payment_channel.in_(("wechat", "wechat_qr")),
        )
    )

    return AdminDashboardOut(
        visits_today=stats["visits_today"],
        visits_7d=stats["visits_7d"],
        visits_30d=stats["visits_30d"],
        orders_total=orders_total,
        orders_paid=orders_paid,
        orders_pending_confirm=int(orders_pending or 0),
        revenue_total=float(revenue or 0),
        users_total=users_total,
        visit_chart=stats["chart"],
        recent_orders=recent,
        pending_payment_orders=pending_orders,
    )


@router.get("/订单", response_model=list[AdminOrderOut], summary="订单列表")
async def list_orders(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
):
    result = await db.execute(
        select(Order).options(selectinload(Order.user)).order_by(Order.created_at.desc()).limit(limit)
    )
    return [_order_out(o) for o in result.scalars().all()]


@router.get("/用户", response_model=list[AdminUserOut], summary="用户列表")
async def list_users(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    q: str = Query(""),
):
    stmt = select(User).order_by(User.id.desc())
    if q.strip():
        stmt = stmt.where(User.username.contains(q.strip()))
    result = await db.execute(stmt)
    return [_user_out(u) for u in result.scalars().all()]


@router.post("/用户", response_model=AdminUserOut, summary="创建用户")
async def create_user(
    body: AdminUserCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    account = body.username.strip()
    exists = await db.execute(select(User).where(User.username == account))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="账号已存在")
    user = User(
        username=account,
        password_hash=pwd_context.hash(body.password),
        tier=body.tier,
        free_quota_used=0,
        quota_limit=body.quota_limit,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _user_out(user)


@router.patch("/用户/{user_id}", response_model=AdminUserOut, summary="更新用户")
async def update_user(
    user_id: int,
    body: AdminUserUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if body.tier is not None:
        user.tier = body.tier
    if body.quota_limit is not None:
        user.quota_limit = body.quota_limit
    if body.free_quota_used is not None:
        user.free_quota_used = body.free_quota_used
    if body.password:
        user.password_hash = pwd_context.hash(body.password)
    await db.commit()
    await db.refresh(user)
    return _user_out(user)


@router.get("/模板", response_model=list[H5TemplateOut], summary="H5 模板列表")
async def admin_list_templates(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    rows = await admin_list(db)
    return [
        H5TemplateOut(**{**r, "premium": bool(r.get("premium")), "enabled": bool(r.get("enabled"))})
        for r in rows
    ]


@router.post("/模板", response_model=H5TemplateOut, summary="创建 H5 模板")
async def admin_create_template(
    body: H5TemplateCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await create_template(db, body.model_dump())
        await db.commit()
    except H5TemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return H5TemplateOut(**{**row, "premium": bool(row.get("premium")), "enabled": bool(row.get("enabled"))})


@router.put("/模板/{template_id}", response_model=H5TemplateOut, summary="更新 H5 模板")
async def admin_update_template(
    template_id: str,
    body: H5TemplateUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await update_template(db, template_id, body.model_dump(exclude_unset=True))
        await db.commit()
    except H5TemplateError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return H5TemplateOut(**{**row, "premium": bool(row.get("premium")), "enabled": bool(row.get("enabled"))})


@router.delete("/模板/{template_id}", summary="删除 H5 模板")
async def admin_delete_template(
    template_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        await delete_template(db, template_id)
        await db.commit()
    except H5TemplateError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "已删除"}


class OrderConfirmRequest(BaseModel):
    admin_remark: str = Field("", max_length=255)


@router.get("/中转额度", response_model=RelayQuotaOut, summary="查询中转 API 账户余额")
async def admin_relay_quota(_admin: User = Depends(require_admin)):
    try:
        info = await fetch_relay_quota()
    except RelayQuotaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return RelayQuotaOut(
        profile=info.profile,
        remaining_label=info.remaining_label,
        remaining_usd=info.remaining_usd,
        used_raw=info.used_raw,
        request_count=info.request_count,
        is_low=info.is_low,
        low_threshold_usd=info.low_threshold_usd,
        recharge_url=info.recharge_url,
        message=info.message,
    )


@router.post("/订单/{order_id}/确认收款", response_model=AdminOrderOut, summary="确认微信收款并开通套餐")
async def admin_confirm_order(
    order_id: int,
    body: OrderConfirmRequest,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    try:
        await confirm_order_payment(db, order, body.admin_remark)
        await db.commit()
        await db.refresh(order)
        result = await db.execute(select(Order).where(Order.id == order.id).options(selectinload(Order.user)))
        order = result.scalar_one()
    except OrderServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _order_out(order)


@router.post("/订单/{order_id}/拒绝收款", response_model=AdminOrderOut, summary="拒绝收款申报")
async def admin_reject_order(
    order_id: int,
    body: OrderConfirmRequest,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    try:
        await reject_order_payment(db, order, body.admin_remark)
        await db.commit()
        await db.refresh(order)
        result = await db.execute(select(Order).where(Order.id == order.id).options(selectinload(Order.user)))
        order = result.scalar_one()
    except OrderServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _order_out(order)
