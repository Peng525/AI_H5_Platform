"""按会员档位解析大模型名称。"""
from app.config import settings

TIER_FREE = frozenset({"free", "免费", "default"})
TIER_PRO = frozenset({"pro", "paid", "premium", "升级", "会员"})


def normalize_tier(tier: str | None) -> str:
    if not tier:
        return "free"
    t = tier.strip().lower()
    if t in TIER_PRO:
        return "pro"
    return "free"


def resolve_text_model(tier: str | None = None) -> str:
    """文稿生成：免费 gemini-3.1-flash，升级 gemini-3-pro。"""
    if normalize_tier(tier) == "pro":
        return settings.llm_model_pro
    return settings.llm_model_free


def resolve_image_model(tier: str | None = None) -> str:
    """配图生成：免费档与文稿同为 Flash，升级后为 Pro。"""
    if normalize_tier(tier) == "pro":
        return settings.llm_image_model_pro
    return settings.llm_image_model_free
