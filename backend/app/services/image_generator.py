"""编辑器 AI 配图服务。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GenerationLog
from app.schemas import GenerateImageRequest
from app.services.llm.image_provider import generate_image
from app.services.llm.provider import LlmError, QuotaLlmError
from app.services.quota import QuotaExceeded, check_and_consume


async def generate_slide_image(
    db: AsyncSession,
    project_id: int,
    body: GenerateImageRequest,
    user_id: int | None = None,
) -> dict:
    try:
        await check_and_consume(db, user_id, body.tier)
    except QuotaExceeded as exc:
        raise QuotaLlmError(str(exc)) from exc

    try:
        image_url, channel, model, width, height = await generate_image(
            body.prompt,
            body.channel,
            body.tier,
            body.style,
            body.fit_mode,
            body.viewport_width,
            body.viewport_height,
            body.viewport_preset_id,
            body.use_reference_image,
            body.reference_image_url,
        )
    except LlmError as exc:
        await _log(db, project_id, body.channel or "auto", False, str(exc))
        raise

    await _log(db, project_id, channel, True, f"配图成功 · 模型 {model}", model=model)
    await db.commit()
    return {
        "image_url": image_url,
        "channel": channel,
        "model": model,
        "width": width,
        "height": height,
    }


async def generate_standalone_image(
    db: AsyncSession,
    body: GenerateImageRequest,
    user_id: int | None = None,
) -> dict:
    try:
        await check_and_consume(db, user_id, body.tier)
    except QuotaExceeded as exc:
        raise QuotaLlmError(str(exc)) from exc

    try:
        image_url, channel, model, width, height = await generate_image(
            body.prompt,
            body.channel,
            body.tier,
            body.style,
            body.fit_mode,
            body.viewport_width,
            body.viewport_height,
            body.viewport_preset_id,
            body.use_reference_image,
            body.reference_image_url,
        )
    except LlmError as exc:
        await _log(db, None, body.channel or "auto", False, str(exc))
        raise

    await _log(db, None, channel, True, f"独立生图成功 · 模型 {model}", model=model)
    await db.commit()
    return {
        "image_url": image_url,
        "channel": channel,
        "model": model,
        "width": width,
        "height": height,
    }


async def _log(
    db: AsyncSession,
    project_id: int | None,
    channel: str | None,
    success: bool,
    message: str,
    model: str = "",
) -> None:
    db.add(
        GenerationLog(
            project_id=project_id,
            template_id="image_gen",
            channel=channel or "auto",
            model=model or "",
            success=1 if success else 0,
            message=message[:2000],
        )
    )
