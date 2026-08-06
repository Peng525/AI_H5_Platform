# H5 高质量演示 — ppt-master → 导入标准工作流

> **适用**：需要接近 ppt-master 版式质量、避免 H5 在线「快速生成」的溢出与模板感。  
> **关联**：[benchmark-runbook.md](./benchmark-runbook.md) · [h5-vs-ppt-master-compare.md](./h5-vs-ppt-master-compare.md) · [系统架构.md](../系统架构.md) · [ppt-master-worker.md](../ppt-master-worker.md)

---

## 两条生成路径

| 路径 | 入口 | 耗时 | 质量 | 适用 |
|------|------|------|------|------|
| **快速生成** | `/create/generate` → 编辑提示词 → 生成（无 PPT 模板） | 秒级 | 固定 8 种 layout，易溢出 | 移动端预览、草稿 |
| **高质量（推荐）** | 生成页选 ppt-master 模板 → review → **生成演示文稿** | 数分钟（Worker） | 原生形状、1280×720 | 汇报、交付、分享 |

---

## 平台内全自动流程（Worker）

1. 打开 `/create/generate` → **演示文稿** Tab
2. 选择 **PPT 模板**（结构模板 + 品牌模板）
3. 填写主题 → **继续生成** → review 页微调 → **生成演示文稿**
4. `POST /api/v1/项目/ai-生成-premium` 入队；结果页轮询 `GET ai-生成-premium/{job_id}`
5. 阶段：`queued → preparing → strategist → generating → postprocessing → importing → completed`
6. 完成后自动跳转 `/create/generate/result/{public_id}` 进入编辑器

亦可 **导入 ppt-master 成品**（`.pptx`）作为备用路径。

---

## 手动导出（备用 SOP）

Worker 不可用或需完全按 SKILL 人工控场时：

1. 在 `develop/ppt-master-main` 按 `SKILL.md` 完成生成
2. 从 `projects/<name>/exports/` 取得 `.pptx`
3. Dashboard「导入 PPT」或 `POST /api/v1/项目/premium-导入-pptx`

---

## 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| 轮询长期停在 generating | LLM 慢或单页失败 | 查看 `generation_logs.message`；缩短页数 |
| status=failed | subprocess 或 SVG 无效 | 见 [ppt-master-worker.md](../ppt-master-worker.md) |
| **生成完成但页面全白、仅「第 N 页」** | 旧版将 native PPTX 经 `parse_pptx_bytes` 导入，python-pptx 无法还原 ppt-master DrawingML | **已修复**：Worker 改为从 `svg_final/` 直接导入整页 SVG 为 canvas 图片 |
| H5 快速生成目录页溢出 | 401px 宽条 + 固定 Y 坐标 | 改用高质量路径 |
| 情景页只有灰块 | 配图 API 未配置 | 设 `PPT_MASTER_SKIP_IMAGES=1` 或配置 IMAGE_* |

---

## API 摘要

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/项目/ai-生成-premium` | 提交任务，`ppt_template_id` 必填 |
| GET | `/api/v1/项目/ai-生成-premium/{job_id}` | 轮询 `stage`、`progress`、`project_public_id` |
| POST | `/api/v1/项目/premium-导入-pptx` | 手动导入 PPTX |
