"""Full industry writing rules and prompt templates (from resume-builder-skill)."""
from __future__ import annotations

GLOBAL_WRITING_RULES = """
【通用写作规则】
1. 成就优先，而非职责描述——写做成了什么，不写「负责 XX」。
2. 每条工作经历分点必须使用「**加粗概括**：详细描述」格式。
3. 尽量量化：数字、比例、规模、前后对比（如响应时间 500ms→50ms）。
4. ATS 关键词对齐目标 JD，自然嵌入，不堆砌。
5. 页数策略：≤5 年工作经历优先一页；6-10 年尽量一页；10 年以上不超过两页。
6. 技能避免基础描述（如「熟练使用 Office」），向上拔高一层表述。
7. 职位名称使用行业标准写法，与目标 JD 一致。
""".strip()

ROLE_SNIPPETS: dict[str, str] = {
    "general": """
【通用求职 · 技能侧重】
沟通协作、项目管理、跨部门推进、业务结果与量化成就。

【经历撰写要点】
- 每段经历保留最强 3-5 条分点，突出可验证成果
- 项目/职责用 STAR 思路：情境、任务、行动、结果
- 自我评价 1-2 句，突出核心优势与当前状态
""".strip(),
    "backend": """
【后端工程师 · 技能维度】
- 编程语言：Java / Go / Python / Node 等（按实际填写）
- 框架与中间件：Spring、Dubbo、Kafka、Redis、Nginx 等
- 数据库：MySQL、PostgreSQL、MongoDB、分库分表
- 分布式与高并发：微服务、缓存、消息队列、限流降级
- DevOps & 云：Docker、K8s、CI/CD、AWS/阿里云

【撰写示例】
• **系统架构设计：**主导设计高并发支付系统，日均交易 100 万+，可用性 99.99%
• **性能优化：**核心查询链路响应时间从 500ms 降至 50ms，提升 10 倍
""".strip(),
    "ai-pm": """
【AI 产品经理 · 技能维度】
- AI/LLM 能力：Prompt、RAG、Agent、模型评测与落地
- 产品方法论：需求分析、用户研究、Roadmap、PRD
- 数据能力：指标设计、A/B 测试、漏斗与留存分析
- 行业认知：目标赛道业务理解与竞品判断
- 工具协作：Figma、Axure、SQL、协作与项目管理工具

【撰写要点】
突出 LLM 产品从 0 到 1、准确率/转化提升、跨算法/工程/业务协作
""".strip(),
    "product": """
【产品经理 · 技能维度】
- 需求分析与用户研究
- 数据驱动决策与指标体系
- 跨部门协作与项目管理
- STAR 法则描述需求落地全过程

【撰写要点】
每条需求/项目写清：问题、方案、数据结果（DAU、转化率、营收等）
""".strip(),
    "ops-growth": """
【C 端运营 · 技能维度】
- 用户增长：裂变、活动、留存、复购策略
- 内容策划：选题、制作、分发与转化
- 数据分析：漏斗、留存、ROI、归因
- 平台规则：微信/抖音/小红书等平台玩法
- 工具栈：神策、GrowingIO、Excel/SQL 等

【撰写要点】
突出增长实验、活动 GMV/UV、内容爆款数据、用户生命周期运营
""".strip(),
    "design": """
【视觉设计师 · 技能维度】
- 设计能力：品牌 VI、UI、插画、动效
- 设计工具：Figma、Sketch、C4D、After Effects
- 设计方法论：设计系统、组件库、可用性
- 作品集：附链接或二维码说明

【撰写要点】
每个项目写清：品牌/产品、你的角色、设计产出、业务或体验结果
""".strip(),
    "marketing": """
【市场营销 · 技能维度】
- 品牌策略与定位
- 内容营销与创意战役
- 投放渠道：SEM、信息流、KOL、线下活动
- 数据归因与 ROI 分析

【撰写要点】
突出战役名称、预算规模、曝光/转化/ROI、品牌声量提升
""".strip(),
    "finance": """
【财务分析师 · 技能维度】
- 财务专业：报表分析、预算、成本控制、审计
- 建模与估值：DCF、可比公司、敏感性分析
- 数据工具：Excel 高级、SQL、Power BI / Tableau
- 行业理解：所覆盖行业财务特点

【撰写要点】
突出建模项目、节省成本金额、决策支持案例、报告影响
""".strip(),
    "hr": """
【HRBP · 技能维度】
- 招聘：渠道、面试、Offer 转化、雇主品牌
- OD/绩效/薪酬：体系设计、落地与迭代
- 业务理解：懂业务语言，支持组织变革
- 数据敏感度：人效、离职率、招聘周期等指标

【撰写要点】
突出编制优化、关键岗位交付、绩效改革、组织诊断项目
""".strip(),
    "sales": """
【销售/BD · 技能维度】
- 销售方法论：SPIN、解决方案销售、大客户管理
- 客户类型：ToB / ToG / 渠道 / 海外
- 最大成单规模与年度业绩
- 行业资源与客户网络

【撰写要点】
写清年度/季度业绩、回款、新客户数、续约率、标杆客户案例
""".strip(),
    "data-analyst": """
【数据分析师 · 技能维度】
- SQL / Python 数据处理
- BI 工具：Tableau、Power BI、Looker
- 统计分析：假设检验、回归、预测
- 业务理解：将分析结论转化为行动建议
- 数据可视化与报告呈现

【撰写要点】
突出分析项目、指标体系搭建、业务决策影响、效率提升
""".strip(),
    "campus": """
【校招应届 · 撰写要点】
- 突出实习经历：公司、岗位、具体贡献与量化结果
- 竞赛/项目：ACM、数学建模、创业大赛、课程项目
- 学习能力与主动性，避免空泛形容词
- 一页纸为主，教育背景与实习/项目并重
""".strip(),
}


def build_system_snippet(role_id: str) -> str:
    role = ROLE_SNIPPETS.get(role_id, ROLE_SNIPPETS["general"])
    return f"{GLOBAL_WRITING_RULES}\n\n{role}"


def build_prompt_full(role_id: str, title: str) -> str:
    """Full user-facing prompt template for the optimize input box."""
    common = """
【目标岗位】
（请填写，如：高级后端工程师 / AI 产品经理）

【核心优势】
（请列出 1-2 个最想突出的优势）

【量化成就】
（请补充数字：团队规模、业绩、性能提升、用户增长等）

【优化方向】
（如：对齐 JD 关键词、压缩至一页、强化项目经历等）
""".strip()
    role_hint = ROLE_SNIPPETS.get(role_id, ROLE_SNIPPETS["general"])
    return f"【{title}】\n{role_hint}\n\n{common}"


def prompt_fields(role_id: str) -> list[dict[str, str]]:
    """Structured fields for prompt template cards."""
    snippets = ROLE_SNIPPETS.get(role_id, ROLE_SNIPPETS["general"])
    lines = [ln.strip() for ln in snippets.split("\n") if ln.strip() and not ln.startswith("【")]
    preview = lines[0][:48] + ("…" if len(lines[0]) > 48 else "") if lines else ""
    return [
        {"label": "规则", "value": "加粗概括+冒号、量化成就、ATS 对齐"},
        {"label": "侧重", "value": preview or "岗位技能维度优化"},
    ]
