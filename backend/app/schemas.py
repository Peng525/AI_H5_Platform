"""API 请求/响应模型。"""
import json
from typing import Any

from pydantic import BaseModel, Field


class SlideOut(BaseModel):
    id: int
    sort_order: int
    layout: str
    title: str
    subtitle: str
    bullets: list[str]
    speaker_notes: str
    animation: str
    canvas_elements: list[dict[str, Any]] = Field(default_factory=list)
    chat_script: dict[str, Any] | None = None
    canvas_background: str | None = None

    @classmethod
    def from_orm_slide(cls, slide: Any, canvas_background: str | None = None) -> "SlideOut":
        bullets = json.loads(slide.bullets_json or "[]")
        try:
            canvas_elements = json.loads(getattr(slide, "canvas_json", None) or "[]")
            if not isinstance(canvas_elements, list):
                canvas_elements = []
        except json.JSONDecodeError:
            canvas_elements = []
        chat_script = None
        try:
            parsed = json.loads(getattr(slide, "chat_script_json", None) or "{}")
            if isinstance(parsed, dict) and (parsed.get("enabled") or parsed.get("timeline") or parsed.get("messages")):
                chat_script = parsed
        except json.JSONDecodeError:
            chat_script = None
        return cls(
            id=slide.id,
            sort_order=slide.sort_order,
            layout=slide.layout,
            title=slide.title,
            subtitle=slide.subtitle,
            bullets=bullets,
            speaker_notes=slide.speaker_notes,
            animation=slide.animation,
            canvas_elements=canvas_elements,
            chat_script=chat_script,
            canvas_background=canvas_background,
        )


class ProjectSettingsOut(BaseModel):
    viewportId: str = "mobile-375"
    scrollEffect: str = "page"
    slideBackgrounds: dict[str, str] = Field(default_factory=dict)
    bgm: dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": False,
            "trackId": "",
            "url": "",
            "loop": True,
            "volume": 0.35,
        }
    )
    defaultChatTapToContinue: bool = True
    themeId: str = "zjy-minimal"
    showScrollHint: bool = False


class ProjectSettingsUpdate(BaseModel):
    viewportId: str | None = None
    scrollEffect: str | None = None
    themeId: str | None = None
    showScrollHint: bool | None = None
    slideBackgrounds: dict[str, str] | None = None
    bgm: dict[str, Any] | None = None
    defaultChatTapToContinue: bool | None = None


def parse_project_settings(raw: str | None) -> dict[str, Any]:
    try:
        data = json.loads(raw or "{}")
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {}


def project_settings_out(project: Any) -> ProjectSettingsOut:
    data = parse_project_settings(getattr(project, "settings_json", None))
    bg = data.get("bgm") or {}
    return ProjectSettingsOut(
        viewportId=data.get("viewportId", "mobile-375"),
        scrollEffect=data.get("scrollEffect", "page"),
        slideBackgrounds=data.get("slideBackgrounds") or {},
        bgm={
            "enabled": bool(bg.get("enabled", False)),
            "trackId": bg.get("trackId") or "",
            "url": bg.get("url") or "",
            "loop": bg.get("loop", True) if bg.get("loop") is not False else False,
            "volume": float(bg.get("volume", 0.35)),
        },
        defaultChatTapToContinue=data.get("defaultChatTapToContinue", True),
        themeId=data.get("themeId", "zjy-minimal"),
        showScrollHint=bool(data.get("showScrollHint", False)),
    )


class ProjectOut(BaseModel):
    id: int
    title: str
    theme: str
    share_slug: str | None
    settings: ProjectSettingsOut = Field(default_factory=ProjectSettingsOut)
    slides: list[SlideOut] = []


class ProjectCreate(BaseModel):
    title: str = "未命名演示"
    theme: str = "default"
    template_id: str | None = Field(None, description="H5 探索模板 ID")


class OrderOut(BaseModel):
    id: int
    plan_id: str
    plan_name: str
    amount: float
    payment_channel: str
    status: str
    user_remark: str = ""
    admin_remark: str = ""
    created_at: Any | None = None
    claimed_at: Any | None = None
    confirmed_at: Any | None = None
    expires_at: Any | None = None


class OrderClaimRequest(BaseModel):
    remark: str = Field("", max_length=255, description="付款备注（可选，如微信昵称后四位）")


class RelayLinkOut(BaseModel):
    recharge_url: str = ""
    configured: bool = False
    message: str = ""


class H5TemplateOut(BaseModel):
    id: str
    title: str
    description: str = ""
    category: str = ""
    device: str = "mobile"
    pages: int = 1
    premium: bool = False
    cover_gradient: str = ""
    default_viewport: str = "mobile-375"
    slides_json: list[dict[str, Any]] = Field(default_factory=list)
    settings_json: dict[str, Any] = Field(default_factory=dict)
    sort_order: int = 0
    enabled: bool = True
    featured: bool = False


class H5TemplateCreate(BaseModel):
    id: str = Field(..., min_length=2, max_length=64)
    title: str
    description: str = ""
    category: str = ""
    device: str = "mobile"
    pages: int = 1
    premium: bool = False
    cover_gradient: str = "from-primary to-primary-container"
    default_viewport: str = "mobile-375"
    slides_json: list[dict[str, Any]] = Field(default_factory=list)
    settings_json: dict[str, Any] = Field(default_factory=dict)
    sort_order: int = 0
    enabled: bool = True


class H5TemplateUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    device: str | None = None
    pages: int | None = None
    premium: bool | None = None
    cover_gradient: str | None = None
    default_viewport: str | None = None
    slides_json: list[dict[str, Any]] | None = None
    settings_json: dict[str, Any] | None = None
    sort_order: int | None = None
    enabled: bool | None = None


class LayoutBlockOut(BaseModel):
    id: str
    label: str
    icon: str = "dashboard"
    group: str = "custom"
    placement: str = "more"
    elements: list[dict[str, Any]] = Field(default_factory=list)
    elements_web: list[dict[str, Any]] = Field(default_factory=list)
    canvas_background: str = ""
    sort_order: int = 100
    enabled: bool = True
    source: str = "admin"


class LayoutBlockCreate(BaseModel):
    id: str = Field(..., min_length=2, max_length=64)
    label: str
    icon: str = "dashboard"
    group: str = "custom"
    placement: str = "more"
    elements: list[dict[str, Any]] = Field(default_factory=list)
    elements_web: list[dict[str, Any]] = Field(default_factory=list)
    canvas_background: str = ""
    sort_order: int = 100
    enabled: bool = True


class LayoutBlockUpdate(BaseModel):
    label: str | None = None
    icon: str | None = None
    group: str | None = None
    placement: str | None = None
    elements: list[dict[str, Any]] | None = None
    elements_web: list[dict[str, Any]] | None = None
    canvas_background: str | None = None
    sort_order: int | None = None
    enabled: bool | None = None


class ImagePromptField(BaseModel):
    label: str
    value: str


class ImagePromptTemplateOut(BaseModel):
    id: str
    title: str
    description: str = ""
    fields: list[ImagePromptField] = Field(default_factory=list)
    sort_order: int = 100
    enabled: bool = True
    source: str = "admin"


class ImagePromptTemplatePublicOut(BaseModel):
    id: str
    title: str
    description: str = ""
    fields: list[ImagePromptField] = Field(default_factory=list)


class ImagePromptTemplateCreate(BaseModel):
    id: str = Field(..., min_length=2, max_length=64)
    title: str
    description: str = ""
    fields: list[ImagePromptField] = Field(default_factory=list)
    sort_order: int = 100
    enabled: bool = True


class ImagePromptTemplateUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    fields: list[ImagePromptField] | None = None
    sort_order: int | None = None
    enabled: bool | None = None


class PromptTemplateOut(BaseModel):
    id: str
    name: str
    description: str = ""
    file: str = ""
    system: str = ""
    user: str = ""
    builtin: bool = False


class PromptTemplateCreate(BaseModel):
    id: str = Field(..., min_length=2, max_length=64)
    name: str
    description: str = ""
    system: str
    user: str = ""


class PromptTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    system: str | None = None
    user: str | None = None


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
    chat_script: dict[str, Any] | None = None


class SlideCanvasUpdate(BaseModel):
    elements: list[dict[str, Any]] = Field(default_factory=list)


class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., description="画面描述")
    channel: str | None = None
    tier: str = Field("free", description="会员档位：free 免费 | pro 升级")
    style: str | None = Field(None, description="画面风格标签")
    fit_mode: str | None = Field(None, description="width | fill | original，影响生图比例与提示词")
    viewport_preset_id: str | None = Field(None, description="生图分辨率预设 id")
    viewport_width: int | None = Field(None, description="内容区宽度")
    viewport_height: int | None = Field(None, description="内容区高度")


class GenerateImageResponse(BaseModel):
    image_url: str
    channel: str
    model: str
    width: int = 1024
    height: int = 1024


class LlmSettingsOut(BaseModel):
    default_channel: str
    auto_order: str
    relay_configured: bool
    official_configured: bool
    model_free: str = Field(description="免费档配图（兼容字段）")
    model_pro: str = Field(description="升级档配图（兼容字段）")
    image_model_free: str
    image_model_pro: str
    relay_model: str
    official_model: str


class LlmSettingsAdminOut(LlmSettingsOut):
    timeout: float
    free_quota_per_user: int
    relay_base_url: str
    relay_api_key_masked: str
    official_base_url: str
    official_api_key_masked: str


class LlmSettingsUpdate(BaseModel):
    default_channel: str | None = None
    auto_order: str | None = None
    timeout: float | None = None
    free_quota_per_user: int | None = None
    relay_base_url: str | None = None
    relay_api_key: str | None = None
    relay_model: str | None = None
    official_base_url: str | None = None
    official_api_key: str | None = None
    official_model: str | None = None
    model_free: str | None = None
    model_pro: str | None = None
    image_model_free: str | None = None
    image_model_pro: str | None = None


class LlmTestResult(BaseModel):
    success: bool
    channel: str
    model: str = ""
    message: str
