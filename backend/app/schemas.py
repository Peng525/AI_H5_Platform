"""API 请求/响应模型。"""
import json
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SlideOut(BaseModel):
    id: int
    sort_order: int
    layout: str
    title: str
    subtitle: str
    bullets: list[str]
    speaker_notes: str
    animation: str

    @classmethod
    def from_orm_slide(cls, slide: Any) -> "SlideOut":
        bullets = json.loads(slide.bullets_json or "[]")
        return cls(
            id=slide.id,
            sort_order=slide.sort_order,
            layout=slide.layout,
            title=slide.title,
            subtitle=slide.subtitle,
            bullets=bullets,
            speaker_notes=slide.speaker_notes,
            animation=slide.animation,
        )


class ProjectOut(BaseModel):
    id: int
    title: str
    theme: str
    share_slug: str | None
    slides: list[SlideOut] = []


class ProjectCreate(BaseModel):
    title: str = "未命名演示"
    theme: str = "default"


class ProjectUpdate(BaseModel):
    title: str | None = None
    theme: str | None = None


class SlideCreate(BaseModel):
    layout: str = "bullets"
    title: str = ""
    subtitle: str = ""
    bullets: list[str] = Field(default_factory=list)
    speaker_notes: str = ""
    animation: str = "fade"


class SlideUpdate(BaseModel):
    layout: str | None = None
    title: str | None = None
    subtitle: str | None = None
    bullets: list[str] | None = None
    speaker_notes: str | None = None
    animation: str | None = None
    sort_order: int | None = None


class GenerateFullRequest(BaseModel):
    topic: str = Field(..., description="演示主题")
    audience: str = "通用受众"
    page_count: int = Field(5, ge=1, le=30)
    style: str = "专业简约"
    channel: str | None = None
    tier: str = Field("free", description="会员档位：free 免费 | pro 升级")


class GeneratePageRequest(BaseModel):
    instruction: str = Field(..., description="修改指令")
    channel: str | None = None
    tier: str = Field("free", description="会员档位：free 免费 | pro 升级")


class LlmSettingsOut(BaseModel):
    default_channel: str
    auto_order: str
    relay_configured: bool
    official_configured: bool
    model_free: str = Field(description="免费档：文稿与免费配图")
    model_pro: str = Field(description="升级档")
    image_model_free: str
    image_model_pro: str
    relay_model: str
    official_model: str


class LlmTestResult(BaseModel):
    success: bool
    channel: str
    model: str = ""
    message: str


class DeckJson(BaseModel):
    title: str
    theme: str
    slides: list[dict[str, Any]]

    @field_validator("slides")
    @classmethod
    def slides_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("slides 不能为空")
        return v
