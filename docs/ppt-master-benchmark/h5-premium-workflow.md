# H5 高质量演示 — ppt-master → 导入标准工作流

> **适用**：需要接近 ppt-master 版式质量、避免 H5 在线「快速生成」的溢出与模板感。  
> **关联**：[benchmark-runbook.md](./benchmark-runbook.md) · [h5-vs-ppt-master-compare.md](./h5-vs-ppt-master-compare.md) · [系统架构.md](../系统架构.md)

---

## 两条生成路径

| 路径 | 入口 | 耗时 | 质量 | 适用 |
|------|------|------|------|------|
| **快速生成** | `/create/generate` → 编辑提示词 → 生成 | 秒级 | 固定 8 种 layout，易溢出 | 移动端预览、草稿 |
| **高质量（推荐）** | ppt-master Skill → 导出 PPTX → H5 导入 | 10–20 分钟 | 原生形状、1280×720 | 汇报、交付、分享 |

---

## 高质量工作流（Phase A SOP）

### 1. 在 ppt-master 中生成

1. 打开仓库子目录 `develop/ppt-master-main`（或 [Quick Start](https://github.com/hugohe3/ppt-master#quick-start)）
2. 在 Cursor 中加载 `skills/ppt-master/SKILL.md`，按 Strategist → Executor 流程完成 **Eight Confirmations**
3. 跑完 post-processing，在 `projects/<name>/exports/` 取得 **`.pptx`**

### 2. 导入 H5 平台

任选其一：

- **Dashboard** →「导入 PPT」→ 选择 `.pptx`
- **生成页** →「高质量演示」卡片 →「导入 ppt-master 成品」
- **API**：`POST /api/v1/项目/premium-导入-pptx`（`device=web`，推荐 16:9）

导入后项目 `settings.viewportId` 为 `web-1280`，可在编辑器中继续微调、发布分享。

### 3. 验收

- 打开编辑器：无大面积文字裁切、元素不超出画布
- 对比同主题 H5「快速生成」deck，按 [evaluation-rubric.md](./evaluation-rubric.md) Phase1 维度 1–6 打分

---

## 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| H5 快速生成目录页溢出 | 401px 宽条 + 固定 Y 坐标 | 改用高质量路径；或等新项目默认 1280×720 |
| 情景页只有灰块 | 配图 API 失败 | ppt-master Image_Generator 或导入前手动补图 |
| 导入后样式变样 | PPTX 解析为 canvas 元素 | 预期行为；复杂动画以 ppt-master 导出为准 |

---

## 后续（Phase C）

`POST /api/v1/项目/ai-生成-premium` 将排队服务端 ppt-master Worker；当前版本返回 `awaiting_pptx` 状态，请按上文 SOP 手动导入。
