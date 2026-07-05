"""管理员 API。"""
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.deps.security import pwd_context
from app.database import get_db
from app.deps.auth import is_admin_user, require_admin
from app.models import GenerationLog, Order, Project, User
from app.schemas import (
    AdminGenerationLogListOut,
    AdminGenerationLogOut,
    H5TemplateCreate,
    H5TemplateOut,
    H5TemplateUpdate,
    ImagePromptTemplateCreate,
    ImagePromptTemplateOut,
    ImagePromptTemplateUpdate,
    DeckPromptTemplateCreate,
    DeckPromptTemplateOut,
    DeckPromptTemplateUpdate,
    LayoutBlockCreate,
    LayoutBlockOut,
    LayoutBlockUpdate,
    LayoutDraftOut,
    LayoutDraftStartBody,
    LayoutSaveFromProjectRequest,
    RelayLinkOut,
    TemplateDraftOut,
    TemplatePresetSaveRequest,
)
from app.services.h5_template_service import (
    H5TemplateError,
    admin_list,
    create_template,
    delete_template,
    get_template,
    update_template,
)
from app.services.layout_draft_service import (
    LayoutDraftError,
    get_or_create_layout_draft,
    quick_create_layout_draft,
    save_layout_from_project,
)
from app.services.layout_block_service import (
    LayoutBlockError,
    admin_list as admin_list_layouts,
    create_block,
    delete_block,
    get_block,
    update_block,
)
from app.services.image_prompt_template_service import (
    ImagePromptTemplateError,
    admin_list as admin_list_image_prompts,
    create_template as create_image_prompt_template,
    delete_template as delete_image_prompt_template,
    get_template as get_image_prompt_template,
    update_template as update_image_prompt_template,
)
from app.services.deck_prompt_template_service import (
    DeckPromptTemplateError,
    admin_list as admin_list_deck_prompts,
    create_template as create_deck_prompt_template,
    delete_template as delete_deck_prompt_template,
    get_template as get_deck_prompt_template,
    update_template as update_deck_prompt_template,
)
from app.services.pptx_template_parser import PptxParseError, parse_pptx_bytes
from app.services.template_draft_service import (
    TemplateDraftError,
    apply_parsed_template_to_draft,
    get_or_create_template_draft,
    quick_create_template_draft,
    save_template_preset,
)
from app.services.order_service import (
    OrderServiceError,
    confirm_order_payment,
    delete_expired_orders,
    expire_stale_orders,
    get_order_by_id,
    list_pending_wechat_orders,
    reject_order_payment,
)
from app.services.quota import quota_remaining, quota_total
from app.services.relay_quota_service import get_relay_recharge_link
from app.services.visits import visit_stats

router = APIRouter(prefix="/api/v1/管理", tags=["管理"])

ORDER_STATUS_FILTER = frozenset({"paid", "expired", "pending", "claimed", "rejected", "failed"})


class AdminUserOut(BaseModel):
    id: int
    username: str
    tier: str
    quota_used: int
    quota_total: int
    quota_remaining: int
    is_admin: bool = False
    created_at: datetime | None = None


class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6)
    tier: str = Field("free", description="free | pro")
    quota_limit: int | None = Field(None, description="免费档配额上限，留空用系统默认")
    is_admin: bool = False


class AdminUserUpdate(BaseModel):
    tier: str | None = None
    quota_limit: int | None = None
    free_quota_used: int | None = Field(None, ge=0)
    password: str | None = Field(None, min_length=6)
    is_admin: bool | None = None


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


class BulkDeleteExpiredOut(BaseModel):
    deleted: int


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
        is_admin=is_admin_user(user),
        created_at=user.created_at,
    )


async def _ensure_admin_remains(db: AsyncSession, target: User, new_is_admin: bool) -> None:
    if new_is_admin:
        return
    old_flag = target.is_admin
    target.is_admin = False
    result = await db.execute(select(User))
    has_any = any(is_admin_user(u) for u in result.scalars().all())
    target.is_admin = old_flag
    if not has_any:
        raise HTTPException(status_code=400, detail="至少需要保留一名管理员")


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
    await expire_stale_orders(db)
    await db.commit()
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

    pending_orders_raw = await list_pending_wechat_orders(db, limit=10)
    pending_orders = [_order_out(o) for o in pending_orders_raw]
    orders_pending = len(pending_orders_raw)

    return AdminDashboardOut(
        visits_today=stats["visits_today"],
        visits_7d=stats["visits_7d"],
        visits_30d=stats["visits_30d"],
        orders_total=orders_total,
        orders_paid=orders_paid,
        orders_pending_confirm=orders_pending,
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
    status: str | None = Query(None, description="按状态筛选：paid / expired / pending / claimed / rejected / failed"),
):
    if status is not None and status not in ORDER_STATUS_FILTER:
        raise HTTPException(status_code=400, detail="无效的订单状态")
    stmt = select(Order).options(selectinload(Order.user)).order_by(Order.created_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(Order.status == status)
    result = await db.execute(stmt)
    return [_order_out(o) for o in result.scalars().all()]


@router.delete("/订单/超时", response_model=BulkDeleteExpiredOut, summary="批量删除已超时订单")
async def admin_delete_expired_orders(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_expired_orders(db)
    await db.commit()
    return BulkDeleteExpiredOut(deleted=deleted)


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
        is_admin=body.is_admin,
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
    if body.is_admin is not None:
        await _ensure_admin_remains(db, user, body.is_admin)
        user.is_admin = body.is_admin
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


@router.get("/模板/{template_id}", response_model=H5TemplateOut, summary="H5 模板详情")
async def admin_get_template(
    template_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    row = await get_template(db, template_id)
    if not row:
        raise HTTPException(status_code=404, detail="模板不存在")
    return H5TemplateOut(**{**row, "premium": bool(row.get("premium")), "enabled": bool(row.get("enabled"))})


@router.post("/模板/解析-pptx", response_model=H5TemplateOut, summary="解析 PPTX 为模板草稿")
async def admin_parse_pptx_template(
    file: UploadFile = File(...),
    device: str = Form("mobile"),
    category: str = Form("简约商务"),
    title: str = Form(""),
    _admin: User = Depends(require_admin),
):
    if not file.filename or not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="请上传 .pptx 文件")
    raw = await file.read()
    inferred_title = title.strip() or (file.filename.rsplit(".", 1)[0] if file.filename else "导入模板")
    try:
        parsed = parse_pptx_bytes(raw, device=device if device in ("mobile", "web") else "mobile", title=inferred_title, category=category)
    except PptxParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return H5TemplateOut(**{**parsed, "premium": bool(parsed.get("premium")), "enabled": bool(parsed.get("enabled")), "featured": len(parsed.get("slides_json") or []) > 0})


@router.post("/模板/导入-pptx", response_model=H5TemplateOut, summary="上传 PPTX 并发布为模板")
async def admin_import_pptx_template(
    file: UploadFile = File(...),
    device: str = Form("mobile"),
    category: str = Form("简约商务"),
    title: str = Form(""),
    template_id: str = Form(""),
    enabled: bool = Form(True),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="请上传 .pptx 文件")
    raw = await file.read()
    inferred_title = title.strip() or (file.filename.rsplit(".", 1)[0] if file.filename else "导入模板")
    try:
        parsed = parse_pptx_bytes(raw, device=device if device in ("mobile", "web") else "mobile", title=inferred_title, category=category)
    except PptxParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if template_id.strip():
        parsed["id"] = template_id.strip()
    parsed["enabled"] = enabled
    try:
        row = await create_template(db, parsed)
        await db.commit()
    except H5TemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return H5TemplateOut(**{**row, "premium": bool(row.get("premium")), "enabled": bool(row.get("enabled"))})


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


@router.post("/模板/快速创建", response_model=TemplateDraftOut, summary="一键创建空白模板并进入可视化编辑")
async def admin_template_quick_create(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        template_id, project = await quick_create_template_draft(db, admin)
        await db.commit()
    except H5TemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"创建编辑草稿失败：{exc}") from exc
    return TemplateDraftOut(project_public_id=project.public_id, template_id=template_id)


@router.post("/模板/{template_id}/编辑草稿", response_model=TemplateDraftOut, summary="获取或创建模板可视化编辑草稿")
async def admin_template_edit_draft(
    template_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        project = await get_or_create_template_draft(db, template_id, admin)
        await db.commit()
    except TemplateDraftError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"打开编辑草稿失败：{exc}") from exc
    return TemplateDraftOut(project_public_id=project.public_id, template_id=template_id)


@router.post("/模板/{template_id}/保存预设", response_model=H5TemplateOut, summary="将草稿项目保存为 H5 模板预设")
async def admin_template_save_preset(
    template_id: str,
    body: TemplatePresetSaveRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    meta = body.model_dump(exclude={"project_public_id"}, exclude_unset=True)
    try:
        row = await save_template_preset(db, template_id, body.project_public_id, admin, meta or None)
        await db.commit()
    except TemplateDraftError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return H5TemplateOut(**{**row, "premium": bool(row.get("premium")), "enabled": bool(row.get("enabled"))})


@router.post("/模板/{template_id}/导入-pptx", response_model=TemplateDraftOut, summary="PPTX 导入到模板编辑草稿")
async def admin_template_import_pptx_to_draft(
    template_id: str,
    project_public_id: str = Form(...),
    file: UploadFile = File(...),
    device: str = Form("mobile"),
    title: str = Form(""),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="请上传 .pptx 文件")
    raw = await file.read()
    inferred_title = title.strip() or (file.filename.rsplit(".", 1)[0] if file.filename else "导入模板")
    try:
        parsed = parse_pptx_bytes(
            raw,
            device=device if device in ("mobile", "web") else "mobile",
            title=inferred_title,
            category="简约商务",
        )
        await apply_parsed_template_to_draft(db, template_id, project_public_id, admin, parsed)
        await db.commit()
    except PptxParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TemplateDraftError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TemplateDraftOut(project_public_id=project_public_id, template_id=template_id)


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


class LayoutQuickCreateBody(BaseModel):
    id: str | None = Field(None, max_length=64)
    label: str = "新版式"
    group: str = "custom"
    placement: str = "more"


@router.post("/版式/快速创建", response_model=LayoutDraftOut, summary="一键创建空白版式并进入可视化编辑")
async def admin_layout_quick_create(
    body: LayoutQuickCreateBody | None = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    payload = body or LayoutQuickCreateBody()
    try:
        layout_id, project = await quick_create_layout_draft(
            db,
            admin,
            block_id=payload.id,
            label=payload.label,
            group=payload.group,
            placement=payload.placement,
        )
        await db.commit()
    except LayoutDraftError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"创建版式草稿失败：{exc}") from exc
    return LayoutDraftOut(project_public_id=project.public_id, layout_id=layout_id)


@router.post("/版式/{block_id}/编辑草稿", response_model=LayoutDraftOut, summary="获取或创建版式可视化编辑草稿")
async def admin_layout_edit_draft(
    block_id: str,
    body: LayoutDraftStartBody | None = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    seed = body.model_dump(exclude_unset=True) if body else None
    try:
        project = await get_or_create_layout_draft(db, block_id, admin, seed=seed)
        await db.commit()
    except LayoutDraftError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"打开版式编辑草稿失败：{exc}") from exc
    return LayoutDraftOut(project_public_id=project.public_id, layout_id=block_id)


@router.post("/版式/{block_id}/保存", response_model=LayoutBlockOut, summary="将草稿项目保存为版式块")
async def admin_layout_save_from_project(
    block_id: str,
    body: LayoutSaveFromProjectRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    meta = body.model_dump(exclude={"project_public_id"}, exclude_unset=True)
    try:
        row = await save_layout_from_project(db, block_id, body.project_public_id, admin, meta or None)
        await db.commit()
    except LayoutDraftError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return LayoutBlockOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.get("/版式", response_model=list[LayoutBlockOut], summary="版式块列表（管理）")
async def admin_list_layout_blocks(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    rows = await admin_list_layouts(db)
    return [LayoutBlockOut(**{**r, "enabled": bool(r.get("enabled"))}) for r in rows]


@router.get("/版式/{block_id}", response_model=LayoutBlockOut, summary="版式块详情")
async def admin_get_layout_block(
    block_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    row = await get_block(db, block_id)
    if not row:
        raise HTTPException(status_code=404, detail="版式不存在")
    return LayoutBlockOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.post("/版式", response_model=LayoutBlockOut, summary="创建版式块")
async def admin_create_layout_block(
    body: LayoutBlockCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await create_block(db, body.model_dump())
        await db.commit()
    except LayoutBlockError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return LayoutBlockOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.put("/版式/{block_id}", response_model=LayoutBlockOut, summary="更新版式块")
async def admin_update_layout_block(
    block_id: str,
    body: LayoutBlockUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await update_block(db, block_id, body.model_dump(exclude_unset=True))
        await db.commit()
    except LayoutBlockError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return LayoutBlockOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.delete("/版式/{block_id}", summary="删除版式块")
async def admin_delete_layout_block(
    block_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        await delete_block(db, block_id)
        await db.commit()
    except LayoutBlockError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "已删除"}


@router.get("/生图提示词", response_model=list[ImagePromptTemplateOut], summary="生图提示词模板列表（管理）")
async def admin_list_image_prompt_templates(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    rows = await admin_list_image_prompts(db)
    return [ImagePromptTemplateOut(**{**r, "enabled": bool(r.get("enabled"))}) for r in rows]


@router.get("/生图提示词/{template_id}", response_model=ImagePromptTemplateOut, summary="生图提示词模板详情")
async def admin_get_image_prompt_template(
    template_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    row = await get_image_prompt_template(db, template_id)
    if not row:
        raise HTTPException(status_code=404, detail="模板不存在")
    return ImagePromptTemplateOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.post("/生图提示词", response_model=ImagePromptTemplateOut, summary="创建生图提示词模板")
async def admin_create_image_prompt_template(
    body: ImagePromptTemplateCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await create_image_prompt_template(db, body.model_dump())
        await db.commit()
    except ImagePromptTemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ImagePromptTemplateOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.put("/生图提示词/{template_id}", response_model=ImagePromptTemplateOut, summary="更新生图提示词模板")
async def admin_update_image_prompt_template(
    template_id: str,
    body: ImagePromptTemplateUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await update_image_prompt_template(db, template_id, body.model_dump(exclude_unset=True))
        await db.commit()
    except ImagePromptTemplateError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ImagePromptTemplateOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.delete("/生图提示词/{template_id}", summary="删除生图提示词模板")
async def admin_delete_image_prompt_template(
    template_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        await delete_image_prompt_template(db, template_id)
        await db.commit()
    except ImagePromptTemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "已删除"}


@router.get("/演示提示词", response_model=list[DeckPromptTemplateOut], summary="演示提示词模板列表（管理）")
async def admin_list_deck_prompt_templates(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    rows = await admin_list_deck_prompts(db)
    return [DeckPromptTemplateOut(**{**r, "enabled": bool(r.get("enabled"))}) for r in rows]


@router.get("/演示提示词/{template_id}", response_model=DeckPromptTemplateOut, summary="演示提示词模板详情")
async def admin_get_deck_prompt_template(
    template_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    row = await get_deck_prompt_template(db, template_id)
    if not row:
        raise HTTPException(status_code=404, detail="模板不存在")
    return DeckPromptTemplateOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.post("/演示提示词", response_model=DeckPromptTemplateOut, summary="创建演示提示词模板")
async def admin_create_deck_prompt_template(
    body: DeckPromptTemplateCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await create_deck_prompt_template(db, body.model_dump())
        await db.commit()
    except DeckPromptTemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DeckPromptTemplateOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.put("/演示提示词/{template_id}", response_model=DeckPromptTemplateOut, summary="更新演示提示词模板")
async def admin_update_deck_prompt_template(
    template_id: str,
    body: DeckPromptTemplateUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await update_deck_prompt_template(db, template_id, body.model_dump(exclude_unset=True))
        await db.commit()
    except DeckPromptTemplateError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DeckPromptTemplateOut(**{**row, "enabled": bool(row.get("enabled"))})


@router.delete("/演示提示词/{template_id}", summary="删除演示提示词模板")
async def admin_delete_deck_prompt_template(
    template_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        await delete_deck_prompt_template(db, template_id)
        await db.commit()
    except DeckPromptTemplateError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "已删除"}


class OrderConfirmRequest(BaseModel):
    admin_remark: str = Field("", max_length=255)


@router.get("/中转充值", response_model=RelayLinkOut, summary="中转平台充值链接")
async def admin_relay_link(_admin: User = Depends(require_admin)):
    info = get_relay_recharge_link()
    return RelayLinkOut(
        recharge_url=info.recharge_url,
        configured=info.configured,
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
    await expire_stale_orders(db, order.user_id)
    await db.refresh(order)
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


@router.get("/生成日志", response_model=AdminGenerationLogListOut, summary="AI 生成记录")
async def admin_list_generation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    username: str = Query("", description="按用户名筛选"),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    base = (
        select(GenerationLog, Project, User)
        .outerjoin(Project, GenerationLog.project_id == Project.id)
        .outerjoin(User, Project.user_id == User.id)
        .order_by(GenerationLog.created_at.desc())
    )
    if username.strip():
        base = base.where(User.username.ilike(f"%{username.strip()}%"))

    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar_one() or 0

    offset = (page - 1) * page_size
    result = await db.execute(base.offset(offset).limit(page_size))
    rows = result.all()

    items = [
        AdminGenerationLogOut(
            id=log.id,
            username=user.username if user else None,
            project_public_id=project.public_id if project else None,
            template_id=log.template_id,
            channel=log.channel,
            model=log.model or "",
            duration_ms=log.duration_ms,
            success=bool(log.success),
            message=log.message or "",
            created_at=log.created_at,
        )
        for log, project, user in rows
    ]
    return AdminGenerationLogListOut(items=items, total=total, page=page, page_size=page_size)
