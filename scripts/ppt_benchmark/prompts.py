"""Fixed benchmark content per prompt type (Phase 1)."""
from __future__ import annotations

PAGE_SPECS: dict[str, list[dict[str, str]]] = {
    "调研": [
        {"file": "01_cover.svg", "title": "封面", "brief": "主标题+副标题「2025 中国 Z 世代现制咖啡消费调研」+ 日期 2025-05"},
        {"file": "02_method.svg", "title": "调研背景与方法", "brief": "n=1200、一线40%/新一线35%/二线25%、问卷+6城深访"},
        {"file": "03_profile.svg", "title": "样本画像", "brief": "18-28岁、性别52:48、学生38%/白领45%/其他17%"},
        {"file": "04_freq.svg", "title": "消费频次与客单价", "brief": "3.2次/周、28.6元+2句解读"},
        {"file": "05_factors.svg", "title": "决策因素", "brief": "口味62%、性价比48%、氛围31%，条形对比图"},
        {"file": "06_brands.svg", "title": "品牌对比", "brief": "瑞幸78%、星巴克71%、库迪54%+竞争结论"},
        {"file": "07_advice.svg", "title": "建议与机会", "brief": "3条可执行建议"},
        {"file": "08_ending.svg", "title": "结语", "brief": "一句话总结+谢谢"},
    ],
    "报告": [
        {"file": "01_cover.svg", "title": "封面", "brief": "星云 SaaS Q1 2025 业务复盘 + Executive Report"},
        {"file": "02_summary.svg", "title": "Executive Summary", "brief": "3条核心结论"},
        {"file": "03_kpi.svg", "title": "KPI 总览", "brief": "ARR 8600万、NRR 112%、CAC 8200、LTV/CAC 4.2"},
        {"file": "04_revenue.svg", "title": "收入结构", "brief": "订阅78%/专业服务15%/其他7%"},
        {"file": "05_growth.svg", "title": "增长驱动", "brief": "新签+扩客+留存三条"},
        {"file": "06_risk.svg", "title": "风险与挑战", "brief": "3项风险"},
        {"file": "07_okr.svg", "title": "Q2 OKR", "brief": "3条 OKR"},
        {"file": "08_ending.svg", "title": "结语", "brief": "下一步重点+谢谢"},
    ],
    "学术": [
        {"file": "01_cover.svg", "title": "封面", "brief": "基于Transformer的医学影像三维分割 + 答辩人张某某 + 导师李某某教授 + 2025-06"},
        {"file": "02_background.svg", "title": "研究背景", "brief": "临床需求2点+技术痛点2点"},
        {"file": "03_review.svg", "title": "文献综述", "brief": "CNN vs Transformer各2句+不足1句"},
        {"file": "04_problem.svg", "title": "问题定义", "brief": "512×512×D输入、肝脾胰标签、Dice≥0.85"},
        {"file": "05_method.svg", "title": "方法", "brief": "ViT-3D encoder、128³ patch、Dice+Boundary loss"},
        {"file": "06_experiment.svg", "title": "实验设计", "brief": "BTCV 30 train/10 val、nnU-Net baseline、Dice/HD95/参数量/推理时间"},
        {"file": "07_contribution.svg", "title": "预期贡献", "brief": "3条贡献（参数量降18%、HD95降12%、开源）"},
        {"file": "08_refs.svg", "title": "参考文献", "brief": "[1]-[5] GB/T 7714占位，DOI待补充"},
    ],
}

REQUIRED_KEYWORDS: dict[str, list[str]] = {
    "调研": ["1200", "3.2", "28.6", "62", "48", "31", "瑞幸", "星巴克", "库迪", "67"],
    "报告": ["8600", "112", "8200", "4.2", "78", "OKR", "ARR", "NRR"],
    "学术": ["Transformer", "Dice", "0.85", "ViT", "nnU-Net", "BTCV", "Boundary", "[1]"],
}

STYLE: dict[str, dict[str, str]] = {
    "调研": {"primary": "#1E3A5F", "accent": "#E85D4C", "executor": "Consultant"},
    "报告": {"primary": "#2D3748", "accent": "#3182CE", "executor": "Consultant_Top"},
    "学术": {"primary": "#1A202C", "accent": "#2B6CB0", "executor": "General"},
}


def build_page_system_prompt(bench_type: str, profile: str) -> str:
    style = STYLE[bench_type]
    return f"""You are generating ONE slide as valid SVG for PPT Master benchmark (Phase 1, Web images only, no AI image API).
Profile/model: {profile}
Type: {bench_type}
Canvas: viewBox="0 0 1280 720" width="1280" height="720"
Colors: primary {style['primary']}, accent {style['accent']}
Language: Simplified Chinese
Rules:
- Output ONLY the complete SVG document starting with <svg and ending with </svg>
- Use <text> elements for all text (editable in PowerPoint)
- No markdown fences, no explanation
- Simple geometric charts OK (rect bars, lines)
- Do not use external image href URLs in Phase 1 (solid fills/gradients only)
- Keep text inside safe margins (40px from edges)
"""


def build_page_user_prompt(bench_type: str, page: dict[str, str]) -> str:
    return f"Generate slide: {page['title']}. Content requirement: {page['brief']}. Filename hint: {page['file']}"
