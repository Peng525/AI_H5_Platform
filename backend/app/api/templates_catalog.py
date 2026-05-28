"""H5 模板库（与 Stitch 原型分类一致）。"""
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/模板库", tags=["模板库"])

_CATALOG = [
    {
        "id": "fin-2024",
        "title": "2024 企业财报数据大屏",
        "description": "专业数据可视化，适合年度总结与经营分析汇报。",
        "category": "年度报告",
        "pages": 12,
        "premium": True,
        "cover_gradient": "from-blue-600 to-indigo-800",
    },
    {
        "id": "tech-launch",
        "title": "极简科技产品发布",
        "description": "极简风格，突出产品核心卖点。",
        "category": "产品发布",
        "pages": 8,
        "premium": False,
        "cover_gradient": "from-slate-700 to-slate-900",
    },
    {
        "id": "resume-creative",
        "title": "高端创意个人微简历",
        "description": "适合设计师与创意从业者。",
        "category": "个人简历",
        "pages": 5,
        "premium": False,
        "cover_gradient": "from-rose-500 to-orange-400",
    },
    {
        "id": "corp-intro",
        "title": "企业品牌介绍",
        "description": "展示企业文化、业务与团队。",
        "category": "企业介绍",
        "pages": 10,
        "premium": False,
        "cover_gradient": "from-emerald-600 to-teal-700",
    },
]

_CATEGORIES = ["全部", "年度报告", "产品发布", "个人简历", "企业介绍"]


@router.get("/分类", summary="模板分类")
async def categories():
    return {"items": _CATEGORIES}


@router.get("", summary="探索模板列表")
async def list_templates(category: str = Query("全部"), q: str = Query("")):
    items = _CATALOG
    if category and category != "全部":
        items = [t for t in items if t["category"] == category]
    if q.strip():
        kw = q.strip().lower()
        items = [t for t in items if kw in t["title"].lower() or kw in t["description"].lower()]
    return {"items": items}


@router.get("/套餐", summary="升级套餐")
async def plans():
    return {
        "items": [
            {"id": "newbie", "name": "新手包", "price": 9.9, "quota": 50, "desc": "50 次官方高速调用"},
            {"id": "sprint", "name": "毕业冲刺包", "price": 19.9, "quota": 100, "desc": "100 次 + 高级模板"},
            {"id": "monthly", "name": "毕业专属包月", "price": 29.9, "quota": -1, "recommended": True, "desc": "无限次官方直连"},
        ]
    }
