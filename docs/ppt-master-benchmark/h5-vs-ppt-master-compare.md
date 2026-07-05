# H5 快速生成 vs ppt-master 导入 — 对照 Benchmark

> 用同一主题、同一页数，对比两条路径，定位「简单 / 丑 / 溢出」根因。

---

## 对照矩阵（每类 8 页）

| 维度 | H5 快速生成 | ppt-master → 导入 H5 |
|------|-------------|----------------------|
| 画布 | 默认 1280×720（2026-07 起 AI 新项目） | 1280×720（16:9） |
| 版式来源 | 8 种 `layout_id` 硬编码 | Agent 手写 SVG → PPTX |
| 文本溢出 | fixed compiler + clamp | 少见（checker + 720 高度） |
| 视觉密度 | 偏卡片/要点 | rhythm + 配图 + 图表 |
| 耗时 | < 1 分钟 | 10–20 分钟 |
| 成本 | 1 配额 | 本地 Agent + LLM（见 model-profiles） |

---

## 标准用例（复制即用）

### 用例 A — 调研类（8 页）

- **主题**：`2026 年企业培训 SaaS 市场格局与选型建议`
- **H5**：`/create/generate` → 10 张 → 快速生成
- **ppt-master**：[`prompt-调研类.md`](./prompt-调研类.md)
- **记录表**：[`results-template.md`](./results-template.md)

**重点观察页**：

1. `toc` + 6 条目录 — H5 是否底边溢出
2. `scene_left` 无图 — 是否灰块 + prompt 占位
3. `key_points` — 是否出现「步骤 N」占位

### 用例 B — 报告类（8 页）

- **主题**：`Q1 产品复盘：增长、留存与下季度 OKR`
- **ppt-master**：[`prompt-报告类.md`](./prompt-报告类.md)

**重点观察**：`chart_left` 图表可读性、Consultant 风层次

### 用例 C — 学术类（8 页）

- **主题**：`基于知识图谱的智能导学系统设计与评估`
- **ppt-master**：[`prompt-学术类.md`](./prompt-学术类.md)

**重点观察**：公式/长段落、breathing 页是否避免卡片墙

---

## 评分（Phase1 Rubric 摘要）

| # | 维度 | H5 典型失分 | ppt-master 典型 |
|---|------|-------------|-----------------|
| 1 | 结构完整 | 页型重复 key_points | 节奏多样 |
| 2 | 视觉层次 | 标题/subtitle 裁切 | 明确层级 |
| 3 | 边界安全 | TOC/页眉溢出 | 边距合规 |
| 4 | 配图质量 | 占位灰块 | AI/搜图完成 |
| 5 | 数据表达 | 简单 bar/pie | 图表模板校准 |
| 6 | 可编辑性 | canvas 元素 | 导入后可编辑 |

完整 rubric：[`evaluation-rubric.md`](./evaluation-rubric.md)

---

## 结果归档

```
develop/docs/ppt-master-benchmark/results/YYYYMMDD-h5-vs-premium-<主题>.md
```

参考已有 Phase1 结果：[`results/20260531-phase1-summary.md`](./results/20260531-phase1-summary.md)
