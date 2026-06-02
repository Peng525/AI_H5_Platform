# AI 生成向导

登录后默认进入 AI 生成流程，支持 **演示文稿**（多页全量生成）与 **生成图片**（独立生图，可裁切复制）两种类型。

## 入口页顶栏

| 区域 | 说明 |
|------|------|
| 左上 | 我的工作台 → `/dashboard` |
| 居中 | 欢迎来到 AI H5 平台 |
| 右上 | 主页、我的工作台、用户头像下拉（帮助/退出） |
| 配额 | **入口页不显示**；点击「下一步」后在后续步骤页显示 |

## 路由与步骤

| 步骤 | 路由 | 说明 |
|------|------|------|
| 1 | `/create/generate` | 选择类型；演示文稿可配置页数、背景、尺寸、语言 |
| 2 | `/create/generate/prompt` | 输入提示词；内置示例可「换一组」 |
| 3 | `/create/generate/review` | 提示编辑器：文本量、内容模式、受众、语气、扩写与附加说明 |
| 完成 | `/editor/:id` | 生成成功后进入三栏编辑器 |

**图片类型**跳过第 2、3 步，进入 `/create/generate/image`；调用 `POST /api/v1/生图/独立`，结果页支持裁切、复制、下载，**不创建项目、不进编辑器**。

## 演示文稿配置项

| 配置 | 选项 | 后端字段 |
|------|------|----------|
| 页数 | 1–10 页 | `page_count` |
| 背景 | 经典白粉 / 浅灰 | `background_preset` → `#fafafa` / `#f0f2f5` |
| 尺寸 | 默认动态 / 传统网页 / 移动端 | `viewport_mode` → `auto` / `web-1280` / `mobile-375` |
| 语言 | 简体中文 / English | `language` |

## 提示编辑器（第 3 步）

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

各按钮的详细交互、草稿字段及发给 LLM 的映射见 [功能开发说明书.md](./功能开发说明书.md#四第-3-步--提示编辑器-creategeneratereview)。

## API

### 独立生图

```
POST /api/v1/生图/独立
Authorization: Bearer <token>
Content-Type: application/json
```

请求体与编辑器配图类似（`prompt`、`viewport_preset_id`、`fit_mode`、`tier`）。响应含 `image_url`，前端在结果页展示并支持裁切/复制/下载。

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

1. 登录后进入 `/create/generate`，见欢迎顶栏、两个类型卡片，**无配额**
2. 演示文稿：配置 → 输入提示词 → 提示编辑器 → 生成 → 编辑器页数与背景正确
3. 生成图片：输入描述 → 生成 → 结果页可裁切/复制/下载，不进编辑器
4. 工作台侧栏可正常进入首页与模板库
