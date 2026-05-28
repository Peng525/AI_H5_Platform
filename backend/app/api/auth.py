"""认证与用户配额 API。"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps.auth import get_current_user, is_admin_user
from app.models import User
from app.services.captcha import verify_captcha_ticket
from app.services.captcha.base import CaptchaError
from app.services.quota import quota_remaining, quota_total
from app.services.sms import get_sms_provider
from app.services.sms.base import SmsError
from app.services.sms.code_store import create_and_store_code, is_phone_account

router = APIRouter(prefix="/api/v1/认证", tags=["认证"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class CaptchaConfigOut(BaseModel):
    provider: str
    app_id: str
    sdk_url: str = "https://turing.captcha.qcloud.com/TJCaptcha.js"


class SendSmsRequest(BaseModel):
    phone: str = Field(..., description="11 位手机号")
    captcha_ticket: str = Field(..., min_length=1)
    captcha_randstr: str = Field(..., min_length=1)


class SendSmsResponse(BaseModel):
    ok: bool = True
    message: str = "验证码已发送"
    cooldown_seconds: int = 60
    dev_code: str | None = Field(None, description="仅 mock 模式返回，便于本地调试")


class AuthRequest(BaseModel):
    account: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6)
    captcha_ticket: str = Field(..., min_length=1)
    captcha_randstr: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    token: str
    user_id: int
    username: str
    tier: str
    is_admin: bool = False
    quota_remaining: int
    quota_total: int


class MeOut(BaseModel):
    user_id: int
    username: str
    tier: str
    is_admin: bool
    quota_remaining: int
    quota_total: int


class QuotaOut(BaseModel):
    tier: str
    quota_used: int
    quota_total: int
    quota_remaining: int
    channel_free: str = "基础通道（免费）· Gemini 3.1 Flash"
    channel_pro: str = "官方原生通道（VIP）· Gemini 3 Pro"


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "127.0.0.1"


def _token_for(user_id: int) -> str:
    from jose import jwt

    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


async def _require_captcha(ticket: str, randstr: str, request: Request) -> None:
    try:
        await verify_captcha_ticket(ticket, randstr, _client_ip(request))
    except CaptchaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _require_email_account(account: str) -> None:
    if is_phone_account(account):
        raise HTTPException(status_code=400, detail="请使用邮箱注册，暂不支持手机号")
    if "@" not in account or len(account) < 5:
        raise HTTPException(status_code=400, detail="请输入有效的邮箱地址")


@router.get("/验证码/配置", response_model=CaptchaConfigOut, summary="验证码前端配置")
async def captcha_config():
    provider = (settings.captcha_provider or "mock").strip().lower()
    app_id = settings.tencent_captcha_app_id.strip() if provider == "tencent" else ""
    return CaptchaConfigOut(provider=provider, app_id=app_id)


@router.post("/验证码/发送", response_model=SendSmsResponse, summary="发送登录短信验证码")
async def send_sms_code(
    body: SendSmsRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await _require_captcha(body.captcha_ticket, body.captcha_randstr, request)
    try:
        code = await create_and_store_code(db, body.phone, "login", _client_ip(request))
        provider = get_sms_provider()
        await provider.send_code(body.phone.strip(), code)
        await db.commit()
    except SmsError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    dev_code = code if (settings.sms_provider or "mock").strip().lower() == "mock" else None
    return SendSmsResponse(cooldown_seconds=settings.sms_send_cooldown_seconds, dev_code=dev_code)


@router.post("/注册", response_model=AuthResponse, summary="注册并登录")
@router.post("/登录", response_model=AuthResponse, summary="登录")
async def login_or_register(body: AuthRequest, request: Request, db: AsyncSession = Depends(get_db)):
    await _require_captcha(body.captcha_ticket, body.captcha_randstr, request)

    account = body.account.strip()
    _require_email_account(account)

    result = await db.execute(select(User).where(User.username == account))
    user = result.scalar_one_or_none()

    if user is not None and not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    if user is None:
        user = User(
            username=account,
            password_hash=pwd_context.hash(body.password),
            tier="free",
            free_quota_used=0,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    return AuthResponse(
        token=_token_for(user.id),
        user_id=user.id,
        username=user.username,
        tier=user.tier,
        is_admin=is_admin_user(user),
        quota_remaining=quota_remaining(user),
        quota_total=quota_total(user),
    )


@router.get("/我", response_model=MeOut, summary="当前登录用户")
async def get_me(user: User = Depends(get_current_user)):
    return MeOut(
        user_id=user.id,
        username=user.username,
        tier=user.tier,
        is_admin=is_admin_user(user),
        quota_remaining=quota_remaining(user),
        quota_total=quota_total(user),
    )


@router.get("/配额", response_model=QuotaOut, summary="当前用户 AI 配额")
async def get_quota(user: User = Depends(get_current_user)):
    total = quota_total(user)
    return QuotaOut(
        tier=user.tier,
        quota_used=user.free_quota_used,
        quota_total=total,
        quota_remaining=quota_remaining(user),
    )
