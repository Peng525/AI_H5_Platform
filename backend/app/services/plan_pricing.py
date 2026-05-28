"""套餐定价：统一按张计价。"""
from dataclasses import dataclass

# 统一使用 gpt-image-2 配图
PRICE_PER_GENERATION = 0.5  # 每张 ¥0.5
MONTHLY_QUOTA = 60
PACK_QUOTA_MIN = 10
PACK_QUOTA_MAX = 50


@dataclass(frozen=True)
class PlanSpec:
    id: str
    name: str
    price: float
    quota: int
    tier: str
    desc: str
    recommended: bool = False
    plan_type: str = "pack"  # pack | monthly


def clamp_pack_quota(quota: int) -> int:
    return max(PACK_QUOTA_MIN, min(PACK_QUOTA_MAX, int(quota)))


def pack_price(quota: int) -> float:
    q = clamp_pack_quota(quota)
    return round(q * PRICE_PER_GENERATION, 1)


def monthly_price() -> float:
    return round(MONTHLY_QUOTA * PRICE_PER_GENERATION, 1)


def resolve_plan(plan_id: str, quota: int | None = None) -> PlanSpec | None:
    if plan_id == "monthly":
        q = MONTHLY_QUOTA
        p = monthly_price()
        return PlanSpec(
            id="monthly",
            name="官方直连包月",
            price=p,
            quota=q,
            tier="pro",
            desc=f"每月 {q} 次 GPT 配图 · 尊享官方直连通道",
            recommended=True,
            plan_type="monthly",
        )
    if plan_id == "custom":
        if quota is None:
            return None
        q = clamp_pack_quota(quota)
        p = pack_price(q)
        return PlanSpec(
            id="custom",
            name=f"AI 配图 {q} 次",
            price=p,
            quota=q,
            tier="free",
            desc=f"{q} 次 GPT 配图 · ¥{PRICE_PER_GENERATION}/张",
            plan_type="pack",
        )
    return None


def pricing_meta() -> dict:
    return {
        "model": "gpt-image-2",
        "price_per_generation": PRICE_PER_GENERATION,
        "pack_quota_min": PACK_QUOTA_MIN,
        "pack_quota_max": PACK_QUOTA_MAX,
        "monthly_quota": MONTHLY_QUOTA,
    }
