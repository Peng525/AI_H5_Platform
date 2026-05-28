"""认证与管理员鉴权。"""
from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User


def is_admin_user(user: User) -> bool:
    allowed = {u.strip() for u in settings.admin_usernames.split(",") if u.strip()}
    return user.username in allowed


async def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = int(payload["sub"])
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录") from exc
    except (JWTError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="登录已失效") from exc

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
