# ppt-master Worker（Premium Deck）

## 概述

演示文稿「高质量」路径在 FastAPI 进程内通过 `app/services/ppt_master_worker/` 完成：

`queued → preparing → strategist → generating → postprocessing → importing → completed`

失败时写入 `failed` 与 `error` 字段，前端结果页轮询展示进度。

## 环境变量

| 变量 | 说明 | 默认 |
|------|------|------|
| `PPT_MASTER_ROOT` | ppt-master 子项目根目录 | 自动探测 `ppt-master-main` |
| `PPT_MASTER_WORKSPACE` | 任务工作区 | `./data/ppt_master_projects` |
| `PPT_MASTER_MAX_CONCURRENT` | 并发 Worker 数 | `1` |
| `PPT_MASTER_SKIP_IMAGES` | 跳过 AI 配图（MVP） | `1` |
| `PPT_MASTER_JOB_TIMEOUT_SEC` | 单任务总超时（秒） | `1800` |

LLM 通道与模型沿用 `LLM_*` 配置；单页超时使用 `LLM_TIMEOUT`。

## API

- `POST /api/v1/项目/ai-生成-premium` — 入队，返回 `job_id`、`stage=queued`
- `GET /api/v1/项目/ai-生成-premium/{job_id}` — 轮询 `stage`、`progress`、`current_page`、`project_public_id`

## 状态存储

`generation_logs.message` JSON，模板 id 为 `premium_deck`。完成后 `success=1` 并关联 `projects.public_id`。

## 进度与 ETA（前端）

- **进度 `progress`**（`job_store.stage_progress`）：`generating` 阶段与页码线性对齐，第 k/n 页 ≈ `round(100 × k/n)%`（上限 90%，导出/导入 92→97→100）。
- **预计总时长（区间）**：规划/准备阶段显示 `formatPremiumDeckRangeLabel(pageCount)`，5 页为 **「6–10 分钟」**（`estimatePremiumDeckRange`：`typical±` 带宽），不再显示单一「8 分 30 秒」。
- **剩余约（阶段加权）**：进入 `generating` 且 `current_page≥1` 后，按 `computeStageAwareRemainingSeconds`（strategist ~15%、generating ~75%、post+import ~10%）估算剩余；**不再**用 `elapsed/(progress/100)` 线性外推（避免 8%→20% 进度跳变导致从 8 分半骤降到 ~2 分）。
- **平滑更新**：`smoothEtaSeconds` 每次轮询（3s）剩余时间最多变化 ±25 秒；副文案说明「剩余时间随当前生成阶段更新，属正常现象」。

典型 5 页 premium 总耗时 **6–10 分钟**（逐页 LLM 写 SVG），与 ppt-master SKILL Executor 阶段同级。

## 导入路径（重要）

Worker 完成 SVG 生成与 `finalize_svg` 后，**不再**将 native PPTX 经 `parse_pptx_bytes` 写入编辑器（python-pptx 无法完整还原 ppt-master 的 DrawingML，会导致空白页与「第 N 页」占位标题）。

当前流程：`svg_final/`（或回退 `svg_output/`）→ 每页整页 SVG 作为 `canvas_elements` 图片 → H5 编辑器 1280×720 预览。

`svg_to_pptx` 仍会尝试导出 PPTX 供归档/手动下载；导出失败不阻断导入。

手动「导入 PPT」仍走 PPTX 解析；`pptx_template_parser` 已递归解析 GROUP 形状以改善兼容。

## 故障排查

1. **`pipeline_available: false`** — 检查 `PPT_MASTER_ROOT` 下是否存在 `skills/ppt-master/SKILL.md`
2. **`svg_to_pptx failed`** — Docker 需安装 `python-pptx`、`svglib`；确认工作区 SVG 已写入 `svg_output/`
3. **Strategist 回退** — LLM 未返回合法 JSON 时使用 deterministic 页计划，日志含 `Strategist LLM fallback`
4. **生成超时** — 减少 `page_count` 或增大 `PPT_MASTER_JOB_TIMEOUT_SEC`
5. **并发 OOM** — 保持 `PPT_MASTER_MAX_CONCURRENT=1`
6. **编辑器全白** — 确认 `generation_logs.message.import_source=svg`；检查工作区 `svg_final/*.svg` 是否有内容

## 相关文档

- `develop/docs/ppt-master-benchmark/h5-premium-workflow.md`
- `develop/docs/系统架构.md` Phase C

## Deck 模板来源

- 内置：`ppt-master-main/skills/ppt-master/templates/decks/`（含 `pptx_template_import` 批量入库）
- 用户上传：`POST /api/v1/演示/ppt-模板/导入` → `data/imported_deck_templates/decks/`
