"""短信验证码存储与限频。"""
import random
import re
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import SmsCode
from app.services.sms.base import SmsError

PHONE_RE = re.compile(r"^1\d{10}$")
_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def normalize_phone(phone: str) -> str:
    p = phone.strip()
    if not PHONE_RE.match(p):
        raise SmsError("请输入有效的 11 位手机号")
    return p


def is_phone_account(account: str) -> bool:
    return bool(PHONE_RE.match(account.strip()))


def _hash_code(code: str) -> str:
    return _pwd.hash(code)


def _verify_code(code: str, code_hash: str) -> bool:
    return _pwd.verify(code, code_hash)


async def create_and_store_code(db: AsyncSession, phone: str, scene: str, ip: str = "") -> str:
    phone = normalize_phone(phone)
    now = datetime.now(timezone.utc)
    cooldown = timedelta(seconds=settings.sms_send_cooldown_seconds)

    last = await db.execute(
        select(SmsCode)
        .where(SmsCode.phone == phone, SmsCode.scene == scene)
        .order_by(SmsCode.created_at.desc())
        .limit(1)
    )
    row = last.scalar_one_or_none()
    if row and row.created_at and (now - row.created_at.replace(tzinfo=timezone.utc)) < cooldown:
        raise SmsError(f"请 {settings.sms_send_cooldown_seconds} 秒后再试")

    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_count = await db.execute(
        select(SmsCode).where(
            SmsCode.phone == phone,
            SmsCode.scene == scene,
            SmsCode.created_at >= day_start,
        )
    )
    if len(day_count.scalars().all()) >= settings.sms_daily_limit_per_phone:
        raise SmsError("今日验证码发送次数已达上限")

    code = f"{random.randint(0, 999999):06d}"
    expires = now + timedelta(minutes=settings.sms_code_ttl_minutes)
    db.add(
        SmsCode(
            phone=phone,
            code_hash=_hash_code(code),
            scene=scene,
            expires_at=expires,
            client_ip=(ip or "")[:64],
        )
    )
    await db.flush()
    return code


async def verify_stored_code(db: AsyncSession, phone: str, code: str, scene: str = "login") -> None:
    phone = normalize_phone(phone)
    if not re.fullmatch(r"\d{6}", code.strip()):
        raise SmsError("请输入 6 位短信验证码")

    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(SmsCode)
        .where(
            SmsCode.phone == phone,
            SmsCode.scene == scene,
            SmsCode.used_at.is_(None),
            SmsCode.expires_at >= now,
        )
        .order_by(SmsCode.created_at.desc())
        .limit(5)
    )
    rows = list(result.scalars().all())
    for row in rows:
        if _verify_code(code.strip(), row.code_hash):
            row.used_at = now
            await db.flush()
            await db.execute(
                delete(SmsCode).where(
                    SmsCode.phone == phone,
                    SmsCode.scene == scene,
                    SmsCode.id != row.id,
                    SmsCode.used_at.is_(None),
                )
            )
            return
    raise SmsError("短信验证码错误或已过期")
