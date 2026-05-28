"""认证与用户配额 API。"""
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps.auth import get_current_user, is_admin_user
from app.models import User
from app.services.quota import quota_remaining, quota_total

router = APIRouter(prefix="/api/v1/认证", tags=["认证"])
# pbkdf2 避免 Docker 内 bcrypt 与 passlib 版本冲突导致 500
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# 演示用：验证码通过前端滑块后传 captcha_ok=true
class AuthRequest(BaseModel):
    account: str = Field(..., description="手机号或邮箱")
    password: str = Field(..., min_length=6)
    captcha_ok: bool = False


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


def _token_for(user_id: int) -> str:
    from jose import jwt

    return jwt.encode({"sub": str(user_id)}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/注册", response_model=AuthResponse, summary="注册并登录")
@router.post("/登录", response_model=AuthResponse, summary="登录")
async def login_or_register(body: AuthRequest, db: AsyncSession = Depends(get_db)):
    if not body.captcha_ok:
        raise HTTPException(status_code=400, detail="请完成拼图验证")
    account = body.account.strip()
    result = await db.execute(select(User).where(User.username == account))
    user = result.scalar_one_or_none()
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
    elif not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")

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
async def get_quota(user_id: int = 1, db: AsyncSession = Depends(get_db)):
    """演示默认 user_id=1；正式版从 JWT 解析。"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(username="demo@local", password_hash=pwd_context.hash("demo123456"), tier="free")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    total = quota_total(user)
    return QuotaOut(
        tier=user.tier,
        quota_used=user.free_quota_used,
        quota_total=total,
        quota_remaining=quota_remaining(user),
    )
