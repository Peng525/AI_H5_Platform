# 横评话术 — 报告类（8 页）

> 使用前：在 [`model-profiles.yaml`](./model-profiles.yaml) 设置 `active_profile`，按 [`benchmark-runbook.md`](./benchmark-runbook.md) 同步 Cursor Models，**新开 Agent 会话**后整段复制发送。

---

## 复制起点（从这里到文末全部粘贴）

请严格按 **PPT Master** 完整工作流生成演示文稿，不要跳过 Strategist 八项确认。

### 横评元信息

- 类型：**报告类**（业务复盘）
- 页数：**严格 8 页**，16:9，不得增减
- 项目目录：`projects/benchmark-{当前 active_profile}-报告-{YYYYMMDD}/`
- 当前横评 profile：请读取 [`model-profiles.yaml`](./model-profiles.yaml) 中的 `active_profile`
- benchmark_phase：
  - **若为 1**：Strategist 配图策略选 **Web-sourced**（Openverse / Pexels，零 AI 生图）
  - **若为 2**：配图使用 **gpt-image-2**（medium，16:9 内容区），与 Phase 1 同一模型

### Executor 与风格

- Executor：**Executor_Consultant_Top**（MBB 咨询风）
- 风格：Executive 商务报告；深灰 `#2D3748` + 蓝 `#3182CE`
- 语言：简体中文（关键 KPI 可保留英文缩写）

### 报告主题与固定 KPI（必须原样使用）

**公司**：星云 SaaS（虚构 B2B 协作软件）

**报告期**：2025 Q1 业务复盘（对比 2024 Q4）

| KPI | 2024 Q4 | 2025 Q1 | QoQ |
|-----|---------|---------|-----|
| ARR（万元） | 4,200 | 4,680 | +11.4% |
| 付费客户数 | 1,850 | 1,972 | +6.6% |
| 毛利率 | 72% | 74% | +2pp |
| CAC（元） | 8,200 | 7,600 | -7.3% |
| LTV/CAC | 3.8 | 4.2 | +0.4 |
| 月流失率 | 2.1% | 1.8% | -0.3pp |
| NPS | 42 | 47 | +5 |

**渠道收入占比 Q1**：直销 58% / 伙伴 27% / 自助 15%

**主要风险（须在「风险」页出现）**：

1. 大客户集中：Top10 客户占 ARR 34%
2. 竞品降价：2 家主要竞品 Q1 宣布年费下调 15%

**下季度 OKR（3 条，须在 OKR 页出现）**：

- O1：ARR 达到 5,100 万（+8.9% QoQ）
- O2：自助渠道占比提升至 20%
- O3：发布 AI 助手 Beta，覆盖 30% 活跃 workspace

### 8 页固定结构

1. **封面**：星云 SaaS · 2025 Q1 业务复盘 | 管理层汇报
2. **Executive Summary**：3 条结论 + 1 条核心风险（各不超过 2 行）
3. **营收与增长**：ARR、客户数、QoQ 表 + 一句解读
4. **成本与毛利**：毛利率 74%、CAC 7,600、LTV/CAC 4.2
5. **渠道对比**：直销 58% / 伙伴 27% / 自助 15%；条形对比
6. **风险与应对**：Top10 集中度 + 竞品降价；各 1 条应对
7. **下季度 OKR**：O1–O3 原文列出
8. **附录/致谢**：数据口径说明（ARR 含年费合同）+ 谢谢

### 禁止项

- 禁止改为 7 页或 9 页
- 禁止编造与 KPI 表冲突的数字
- 禁止跳过导出脚本
- Phase 1 禁止 AI 生图

### 交付要求

1. 完成导出：`exports/` 下生成可编辑 `.pptx`
2. 回复：**总耗时**、**exports 路径**、**版式问题**
3. 图表用 SVG 转形状即可，不要求 Excel 数据绑定

当前横评 profile：见 `model-profiles.yaml` 的 `active_profile`；benchmark_phase 见同文件 `benchmark_phase`。请严格 8 页，导出 exports/，并在完成后列出：耗时、是否改页、主要版式问题。

---

## 复制终点
