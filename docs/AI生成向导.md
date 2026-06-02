# AI 生成向导

登录后默认进入 AI 生成流程，支持 **演示文稿**（多页全量生成）与 **生成图片**（独立生图，可裁切复制）两种类型。

## 入口页顶栏

| 区域 | 说明 |
|------|------|
| 左上 | 主页、我的工作台 |
| 居中 | 欢迎来到 AI H5 平台 |
| 右上 | 用户头像 + 名称；名称下方 `text-xs` 展示 **tier · 配额**（如 `专业版 · 配额 97/100`） |
| 下拉 | 使用帮助、退出登录 |

页面背景为柔和纵向渐变；顶栏半透明毛玻璃。

## 路由与步骤

| 步骤 | 路由 | 说明 |
|------|------|------|
| 1 | `/create/generate` | **Gamma 单页两态**：空态单行输入 + 示例（deck）或 **三胶囊 + 分割线 + 3 张生图模板**（image）；有输入后隐藏示例/模板，居中 **「编辑提示词」** |
| 2 | `/create/generate/review` | 提示编辑器：文本量、内容模式、受众、语气、扩写与附加说明 |
| 完成 | `/editor/:id` | 生成成功后进入三栏编辑器 |

**图片类型** 在生成页选「生成图片」→ 选模板或填写提示词 →「编辑提示词」进入 `/create/generate/image`；调用 `POST /api/v1/生图/独立`，**不创建项目、不进编辑器**。

> `/create/generate/prompt` 已合并至 `/create/generate`，旧链接自动重定向。

## 生成入口两态（`/create/generate`）

| 状态 | 演示文稿 | 生成图片 |
|------|----------|----------|
| 空态 | 顶部胶囊 + 单行输入 + 示例（可换一组） | 顶部胶囊（比例图标/颜色/风格·默认无）+ 输入 + 分割线 + 3 张模板 |
| 有输入 | 胶囊 sticky 固定于输入框上方 + 内容驱动增高 + 居中「编辑提示词」 | 同左（比例/颜色/风格胶囊位置不变） |

- 输入框随内容自动增高（空态上限 ~192px；有输入 ~320px / 35vh，超出框内滚动）
- 胶囊栏 `sticky top-0`，deck / image 均在输入框上方，不贴屏幕最底
- 生图模板与编辑器 AI 面板同源：`IMAGE_PROMPT_TEMPLATES` / 管理端 API
- **开发逻辑**详见 [`生成页组件与开发逻辑.md`](生成页组件与开发逻辑.md)

## 图片生成页（`/create/generate/image`）

顶栏 **返回首页** → `/create/generate`。桌面端 **左右等宽两栏**（`lg:grid-cols-2`），窄屏上下堆叠。

| 左栏 · 提示词编辑 | 右栏 · 生成结果 |
|-------------------|-----------------|
| 提示词 textarea（预填生成页 `topic`） | 展示本次生成所用提示词 |
| 尺寸：`ImageAspectRatioSelect`（1:1 … 9:16 图标+比例） | 图片预览框（空态 / 加载 spinner / 结果） |
| **生成图片**（旋转加载） | **点击图片** → 裁切弹窗 |
| | **复制** → 剪贴板 |

## 演示文稿配置项

| 配置 | 选项 | 后端字段 |
|------|------|----------|
| 页数 | 1–10 张卡片 | `page_count` |
| 背景 | 经典白粉 / 浅灰 | `background_preset` → `#fafafa` / `#f0f2f5` |
| 尺寸 | 默认动态 / 传统网页 / 移动端 | `viewport_mode` → `auto` / `web-1280` / `mobile-375` |
| 语言 | 简体中文 / English | `language` |

## 提示编辑器（第 2 步）

| 设置 | 说明 | 后端字段 |
|------|------|----------|
| 文本量 | 简约 / 精炼 / 详细 / 繁琐 | `text_density` |
| 写给… | 目标受众 | `audience` |
| 语气 | 如「专业、清晰、具说服力」 | `tone` |
| 内容模式 | 自由形式 / 逐张卡片 | `content_mode` |
| 内容（自由形式） | 完整提示词，AI 自行分页 | `extra_content` |
| 内容（逐张卡片） | N 个页面文本框，1:1 映射 | `page_contents[]` |
| 附加说明 | 可选补充 | `extra_instructions` |

### 内容模式说明

| 模式 | 行为 |
|------|------|
| **自由形式**（默认） | 单文本框展示完整内容；生成时 LLM 按 `page_count` 与风格自行分页 |
| **逐张卡片** | 切换时弹窗选「自动分页」或「自行分页」；自动分页按标题/序号/段落拆成 N 框；生成时严格逐页 1:1 |

底栏可微调页数，点击 **生成** 调用全量生成 API。

各按钮的详细交互、草稿字段及发给 LLM 的映射见 [功能开发说明书.md](./功能开发说明书.md#四提示编辑器-creategeneratereview)。

## API

### 独立生图

```
POST /api/v1/生图/独立
Authorization: Bearer <token>
Content-Type: application/json
```

请求体与编辑器配图类似（`prompt`、`viewport_preset_id`、`fit_mode`、`tier`）。响应含 `image_url`，前端在右栏预览框展示；支持点击图片裁切、底部「复制」写入剪贴板。

### 全量生成演示

```
POST /api/v1/项目/ai-生成
Authorization: Bearer <token>
Content-Type: application/json
```

请求体示例：

```json
{
  "topic": "2025 企业数字化转型季度复盘",
  "page_count": 10,
  "audience": "企业管理层",
  "tone": "专业、清晰、具说服力",
  "text_density": "精炼",
  "language": "简体中文",
  "viewport_mode": "auto",
  "background_preset": "classic_white",
  "extra_content": "",
  "extra_instructions": "",
  "content_mode": "free",
  "page_contents": []
}
```

`content_mode: "per_page"` 时 `page_contents` 长度须等于 `page_count`。

响应：`ProjectOut`（含 `slides` 与 `settings`），前端写入 localStorage 后跳转编辑器。

### 相关实现

| 层级 | 路径 |
|------|------|
| 前端向导 | `frontend/src/views/create/` |
| 草稿状态 | `frontend/src/composables/useAiCreateDraft.js`（sessionStorage） |
| 生成服务 | `backend/app/services/deck_generation_service.py` |
| 提示词模板 | `backend/templates/全量生成.yaml` |
| 幻灯片写入 | `backend/app/services/project_seed_service.py` |

## 配额与 LLM 配置

- 每次全量生成消耗 1 次 AI 配额（与配图共用 `check_and_consume`）
- 需在 `.env` 配置 `LLM_RELAY_*` 或 `LLM_OFFICIAL_*`
- 配额不足时 API 返回 402，前端展示错误信息

## 与工作台的关系

| 入口 | 目标 |
|------|------|
| 登录默认 | `/create/generate` |
| 工作台「新建演示」 | `/create/generate` |
| 工作台「首页」 | `/dashboard`（项目列表） |
| 工作台「模板库」 | `/templates` |
| 工作台「导入 PPT」 | 直接上传 `.pptx` → 编辑器 |

## 冒烟检查

完整用例见 **[`生成页测试用例.md`](生成页测试用例.md)**；组件逻辑见 **[`生成页组件与开发逻辑.md`](生成页组件与开发逻辑.md)**。

1. 登录后进入 `/create/generate`：渐变背景、Tab（默认演示文稿）；空态无底部按钮
2. 演示文稿：输入或选示例 →「编辑提示词」→ 提示编辑器 → 生成 → 编辑器页数与背景正确
3. 生成图片：选类型 → 选模板或输入 →「编辑提示词」→ 两栏图片页 → 生成 → 裁切、复制可用
4. 访问 `/create/generate/prompt` 自动回到 `/create/generate`
5. 工作台侧栏可正常进入首页与模板库
