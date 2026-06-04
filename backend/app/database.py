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
        if "tier" not in names:
            sync_conn.execute(text("ALTER TABLE users ADD COLUMN tier VARCHAR(16) DEFAULT 'free'"))
        if "free_quota_used" not in names:
            sync_conn.execute(text("ALTER TABLE users ADD COLUMN free_quota_used INTEGER DEFAULT 0"))
        if "is_admin" not in names:
            sync_conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            from app.config import settings as app_settings

            env_admins = {
                u.strip().lower()
                for u in app_settings.admin_usernames.split(",")
                if u.strip()
            }
            if env_admins:
                for admin_name in env_admins:
                    sync_conn.execute(
                        text("UPDATE users SET is_admin = 1 WHERE lower(username) = :u"),
                        {"u": admin_name},
                    )
        slide_cols = sync_conn.execute(text("PRAGMA table_info(slides)")).fetchall()
        slide_names = {row[1] for row in slide_cols}
        if "canvas_json" not in slide_names:
            sync_conn.execute(text("ALTER TABLE slides ADD COLUMN canvas_json TEXT DEFAULT '[]'"))
        if "chat_script_json" not in slide_names:
            sync_conn.execute(text("ALTER TABLE slides ADD COLUMN chat_script_json TEXT DEFAULT '{}'"))
        if "structured_json" not in slide_names:
            sync_conn.execute(text("ALTER TABLE slides ADD COLUMN structured_json TEXT DEFAULT '{}'"))
        proj_cols = sync_conn.execute(text("PRAGMA table_info(projects)")).fetchall()
        proj_names = {row[1] for row in proj_cols}
        if "settings_json" not in proj_names:
            sync_conn.execute(text("ALTER TABLE projects ADD COLUMN settings_json TEXT DEFAULT '{}'"))
        if "template_source_id" not in proj_names:
            sync_conn.execute(text("ALTER TABLE projects ADD COLUMN template_source_id VARCHAR(64)"))
            sync_conn.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_template_source_id ON projects (template_source_id)"))
        if "public_id" not in proj_names:
            sync_conn.execute(text("ALTER TABLE projects ADD COLUMN public_id VARCHAR(32)"))
            sync_conn.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_public_id ON projects (public_id)"))
            from app.services.deck_generator import new_public_id

            existing_ids = {
                row[0]
                for row in sync_conn.execute(
                    text("SELECT public_id FROM projects WHERE public_id IS NOT NULL AND public_id != ''")
                ).fetchall()
            }
            rows = sync_conn.execute(text("SELECT id, share_slug FROM projects")).fetchall()
            for row_id, share_slug in rows:
                pid = (share_slug or "").strip()
                if not pid:
                    while True:
                        pid = new_public_id()
                        if pid not in existing_ids:
                            break
                elif pid in existing_ids:
                    while True:
                        pid = new_public_id()
                        if pid not in existing_ids:
                            break
                existing_ids.add(pid)
                sync_conn.execute(
                    text("UPDATE projects SET public_id = :pid, share_slug = :pid WHERE id = :id"),
                    {"pid": pid, "id": row_id},
                )
        elif proj_names:
            from app.services.deck_generator import new_public_id

            existing_ids = {
                row[0]
                for row in sync_conn.execute(
                    text("SELECT public_id FROM projects WHERE public_id IS NOT NULL AND public_id != ''")
                ).fetchall()
            }
            rows = sync_conn.execute(
                text("SELECT id, share_slug FROM projects WHERE public_id IS NULL OR public_id = ''")
            ).fetchall()
            for row_id, share_slug in rows:
                pid = (share_slug or "").strip()
                if not pid or pid in existing_ids:
                    while True:
                        pid = new_public_id()
                        if pid not in existing_ids:
                            break
                existing_ids.add(pid)
                sync_conn.execute(
                    text("UPDATE projects SET public_id = :pid, share_slug = COALESCE(NULLIF(share_slug, ''), :pid) WHERE id = :id"),
                    {"pid": pid, "id": row_id},
                )
        tpl_cols = sync_conn.execute(text("PRAGMA table_info(h5_templates)")).fetchall()
        tpl_names = {row[1] for row in tpl_cols}
        if tpl_names and "settings_json" not in tpl_names:
            sync_conn.execute(text("ALTER TABLE h5_templates ADD COLUMN settings_json TEXT DEFAULT '{}'"))
        if tpl_names and "source" not in tpl_names:
            sync_conn.execute(text("ALTER TABLE h5_templates ADD COLUMN source VARCHAR(16) DEFAULT 'file'"))
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
        if "plan_quota" not in order_names:
            sync_conn.execute(text("ALTER TABLE orders ADD COLUMN plan_quota INTEGER"))
        img_tpl_cols = sync_conn.execute(text("PRAGMA table_info(image_prompt_templates)")).fetchall()
        img_tpl_names = {row[1] for row in img_tpl_cols}
        if img_tpl_names and "preview_url" not in img_tpl_names:
            sync_conn.execute(text("ALTER TABLE image_prompt_templates ADD COLUMN preview_url VARCHAR(512) DEFAULT ''"))
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
        gen_cols = sync_conn.execute(text("PRAGMA table_info(generation_logs)")).fetchall()
        gen_names = {row[1] for row in gen_cols}
        if gen_names and "model" not in gen_names:
            sync_conn.execute(text("ALTER TABLE generation_logs ADD COLUMN model VARCHAR(64) DEFAULT ''"))
        if gen_names and "duration_ms" not in gen_names:
            sync_conn.execute(text("ALTER TABLE generation_logs ADD COLUMN duration_ms INTEGER"))
        orphan = sync_conn.execute(text("SELECT id FROM projects WHERE user_id IS NULL")).fetchall()
        if orphan:
            from app.config import settings

            seed_user = (settings.seed_demo_username or "").strip()
            if seed_user:
                demo = sync_conn.execute(
                    text("SELECT id FROM users WHERE username = :u LIMIT 1"),
                    {"u": seed_user},
                ).fetchone()
                if demo:
                    sync_conn.execute(
                        text("UPDATE projects SET user_id = :uid WHERE user_id IS NULL"),
                        {"uid": demo[0]},
                    )

    await conn.run_sync(_run)
