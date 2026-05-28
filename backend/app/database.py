"""数据库连接与会话。"""
import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


def _ensure_data_dir() -> None:
    os.makedirs("data", exist_ok=True)


_ensure_data_dir()
engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _migrate_sqlite_columns(conn)


async def _migrate_sqlite_columns(conn) -> None:
    """SQLite 无 alter 自动迁移，按需补列。"""
    from sqlalchemy import text

    def _run(sync_conn):
        cols = sync_conn.execute(text("PRAGMA table_info(users)")).fetchall()
        names = {row[1] for row in cols}
        if "quota_limit" not in names:
            sync_conn.execute(text("ALTER TABLE users ADD COLUMN quota_limit INTEGER"))
        slide_cols = sync_conn.execute(text("PRAGMA table_info(slides)")).fetchall()
        slide_names = {row[1] for row in slide_cols}
        if "canvas_json" not in slide_names:
            sync_conn.execute(text("ALTER TABLE slides ADD COLUMN canvas_json TEXT DEFAULT '[]'"))
        order_cols = sync_conn.execute(text("PRAGMA table_info(orders)")).fetchall()
        order_names = {row[1] for row in order_cols}
        if "user_remark" not in order_names:
            sync_conn.execute(text("ALTER TABLE orders ADD COLUMN user_remark VARCHAR(255) DEFAULT ''"))
        if "admin_remark" not in order_names:
            sync_conn.execute(text("ALTER TABLE orders ADD COLUMN admin_remark VARCHAR(255) DEFAULT ''"))
        if "claimed_at" not in order_names:
            sync_conn.execute(text("ALTER TABLE orders ADD COLUMN claimed_at DATETIME"))
        if "confirmed_at" not in order_names:
            sync_conn.execute(text("ALTER TABLE orders ADD COLUMN confirmed_at DATETIME"))
        for col, ddl in (
            ("out_trade_no", "ALTER TABLE orders ADD COLUMN out_trade_no VARCHAR(64)"),
            ("transaction_id", "ALTER TABLE orders ADD COLUMN transaction_id VARCHAR(64)"),
            ("prepay_id", "ALTER TABLE orders ADD COLUMN prepay_id VARCHAR(64)"),
            ("code_url", "ALTER TABLE orders ADD COLUMN code_url TEXT"),
            ("paid_at", "ALTER TABLE orders ADD COLUMN paid_at DATETIME"),
            ("notify_raw", "ALTER TABLE orders ADD COLUMN notify_raw TEXT"),
        ):
            if col not in order_names:
                sync_conn.execute(text(ddl))
                order_names.add(col)
        sync_conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS sms_codes ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "phone VARCHAR(16) NOT NULL, "
                "code_hash VARCHAR(255) NOT NULL, "
                "scene VARCHAR(32) DEFAULT 'login', "
                "expires_at DATETIME NOT NULL, "
                "used_at DATETIME, "
                "client_ip VARCHAR(64) DEFAULT '', "
                "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        sync_conn.execute(text("CREATE INDEX IF NOT EXISTS ix_sms_codes_phone ON sms_codes (phone)"))
        orphan = sync_conn.execute(text("SELECT id FROM projects WHERE user_id IS NULL")).fetchall()
        if orphan:
            demo = sync_conn.execute(
                text("SELECT id FROM users WHERE username = :u LIMIT 1"),
                {"u": "demo@ai-h5.com"},
            ).fetchone()
            if demo:
                sync_conn.execute(
                    text("UPDATE projects SET user_id = :uid WHERE user_id IS NULL"),
                    {"uid": demo[0]},
                )

    await conn.run_sync(_run)
