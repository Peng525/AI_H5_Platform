"""H5 模板库（与 Stitch 原型分类一致）。"""
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/模板库", tags=["模板库"])

_CATALOG = [
    {
        "id": "fin-2024-mobile",
        "title": "2024 企业财报数据大屏",
        "description": "专业数据可视化，适合年度总结与经营分析汇报。",
        "category": "年度报告",
        "device": "mobile",
        "pages": 12,
        "premium": True,
        "cover_gradient": "from-blue-600 to-indigo-800",
        "default_viewport": "mobile-375",
    },
    {
        "id": "fin-2024-web",
        "title": "2024 企业财报数据大屏（网页版）",
        "description": "宽屏数据汇报，适合大屏展示与网页嵌入。",
        "category": "年度报告",
        "device": "web",
        "pages": 12,
        "premium": True,
        "cover_gradient": "from-blue-700 to-indigo-900",
        "default_viewport": "web-1920",
    },
    {
        "id": "tech-launch-mobile",
        "title": "极简科技产品发布",
        "description": "极简风格，突出产品核心卖点。",
        "category": "产品发布",
        "device": "mobile",
        "pages": 8,
        "premium": False,
        "cover_gradient": "from-slate-700 to-slate-900",
        "default_viewport": "mobile-375",
    },
    {
        "id": "tech-launch-web",
        "title": "极简科技产品发布（网页版）",
        "description": "1280 宽屏布局，适合官网与发布会投屏。",
        "category": "产品发布",
        "device": "web",
        "pages": 8,
        "premium": False,
        "cover_gradient": "from-slate-800 to-slate-950",
        "default_viewport": "web-1280",
    },
    {
        "id": "resume-creative-mobile",
        "title": "高端创意个人微简历",
        "description": "适合设计师与创意从业者，手机端浏览体验佳。",
        "category": "个人简历",
        "device": "mobile",
        "pages": 5,
        "premium": False,
        "cover_gradient": "from-rose-500 to-orange-400",
        "default_viewport": "mobile-390",
    },
    {
        "id": "resume-creative-web",
        "title": "高端创意个人微简历（网页版）",
        "description": "横向宽屏简历，适合作品集与招聘场景。",
        "category": "个人简历",
        "device": "web",
        "pages": 5,
        "premium": False,
        "cover_gradient": "from-rose-600 to-orange-500",
        "default_viewport": "web-1280",
    },
    {
        "id": "corp-intro-mobile",
        "title": "企业品牌介绍",
        "description": "展示企业文化、业务与团队。",
        "category": "企业介绍",
        "device": "mobile",
        "pages": 10,
        "premium": False,
        "cover_gradient": "from-emerald-600 to-teal-700",
        "default_viewport": "mobile-375",
    },
    {
        "id": "corp-intro-web",
        "title": "企业品牌介绍（网页版）",
        "description": "企业官网风格宽屏介绍，适合 B 端展示。",
        "category": "企业介绍",
        "device": "web",
        "pages": 10,
        "premium": False,
        "cover_gradient": "from-emerald-700 to-teal-800",
        "default_viewport": "web-1920",
    },
]

_CATEGORIES = ["全部", "年度报告", "产品发布", "个人简历", "企业介绍"]
_DEVICES = [
    {"id": "全部", "label": "全部终端"},
    {"id": "mobile", "label": "移动端"},
    {"id": "web", "label": "网页版"},
]


@router.get("/分类", summary="模板分类")
async def categories():
    return {"items": _CATEGORIES, "devices": _DEVICES}


@router.get("", summary="探索模板列表")
async def list_templates(
    category: str = Query("全部"),
    device: str = Query("全部", description="全部 | mobile | web"),
    q: str = Query(""),
):
    items = _CATALOG
    if category and category != "全部":
        items = [t for t in items if t["category"] == category]
    if device and device != "全部":
        items = [t for t in items if t["device"] == device]
    if q.strip():
        kw = q.strip().lower()
        items = [
            t
            for t in items
            if kw in t["title"].lower()
            or kw in t["description"].lower()
            or kw in t["category"].lower()
            or ("移动" in kw and t["device"] == "mobile")
            or ("网页" in kw and t["device"] == "web")
            or ("手机" in kw and t["device"] == "mobile")
        ]
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
