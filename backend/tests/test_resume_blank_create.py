"""Integration test: blank visual-template resume create."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.config import settings
from app.database import Base, _migrate_sqlite_columns
from app.models import ResumeProfile, User
from app.services.resume.resume_service import create_profile
from app.services.resume.visual_compiler import TEMPLATE_CLASSIC_BLUE


class ResumeBlankCreateTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        tmp = Path(self._tmpdir.name)
        settings.resume_data_dir = str(tmp / "resume_data")
        db_path = tmp / "test.db"
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await _migrate_sqlite_columns(conn)
        self.session_factory = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def asyncTearDown(self) -> None:
        await self.engine.dispose()
        self._tmpdir.cleanup()

    async def test_create_profile_blank_classic_blue_writes_version_and_thumbnail(self) -> None:
        async with self.session_factory() as db:
            user = User(username="resume_blank_test@example.com", password_hash="hash", tier="free")
            db.add(user)
            await db.flush()

            profile = await create_profile(db, user, template_id=TEMPLATE_CLASSIC_BLUE)
            await db.commit()
            result = await db.execute(
                select(ResumeProfile)
                .where(ResumeProfile.id == profile.id)
                .options(selectinload(ResumeProfile.versions))
            )
            profile = result.scalar_one()

            self.assertTrue(profile.public_id)
            self.assertEqual(profile.title, "我的简历")
            self.assertTrue(profile.versions)
            self.assertEqual(profile.versions[0].version_no, 1)
            self.assertTrue(profile.versions[0].visual_document_json)
            self.assertTrue(profile.thumbnail_path)

            thumb = Path(settings.resume_data_dir) / profile.thumbnail_path
            self.assertTrue(thumb.is_file())
            self.assertTrue(thumb.read_bytes().startswith(b"\x89PNG"))


if __name__ == "__main__":
    unittest.main()
