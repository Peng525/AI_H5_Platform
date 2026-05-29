# AI 智能 H5 演示平台

类 PPT 的 AI 驱动 H5 演示生成与播放平台。全简体中文界面，支持 **auto / 中转 API / 官方 API** 三种大模型通道，内置 **全量生成** 与 **单页改写** 两套提示词模板。

- GitHub: [Peng525/AI_H5_Platform](https://github.com/Peng525/AI_H5_Platform)
- 开发分支: `develop`

## 数据存储位置

| 内容 | 路径 |
|------|------|
| SQLite 数据库（用户、项目、页面、订单、访问统计） | `develop/data/app.db` |
| Docker 挂载 | 宿主机 `develop/data` → 容器 `/app/backend/data` |
| 环境变量 / API Key | `develop/.env`（**勿提交 Git**） |
| 登录态（浏览器） | `localStorage`：`ai_h5_token`、`ai_h5_user` |

## 演示账号（进入主页 `/templates`）

| 项 | 值 |
|----|-----|
| 账号 | `demo@ai-h5.com` |
| 密码 | `demo123456` |
| 说明 | 勾选「我已完成验证」后点击「注册/登录」 |

## 管理员账号（管理控制台 `/admin`）

| 项 | 值 |
|----|-----|
| 账号 | `admin@ai-h5.com` |
| 密码 | `admin123456` |
| 功能 | 数据仪表盘、用户管理、订单查看、**版式管理**、H5 模板管理、系统设置 |
| 说明 | 登录后自动进入 `/admin`；可创建用户、调整会员与 API 配额 |

普通用户导航栏不显示管理入口。

## 功能概览（P0）

- 项目管理、页面编辑、全屏 H5 预览
- **探索模板**：按模板类型 + 终端筛选；卡片封面渲染**第一页幻灯片**缩略图
- **简约模板体系**：ZJY 商务 + 易企秀叙事双主题，14 种页面版式块，10 套完整 JSON 模板（见下文）
- **背景音乐（BGM）**：动效面板文本按钮启用；曲库来自 `backend/static/bgm/`；画布右上角旋转播放器可静音/继续
- 画布内容自动保存至服务端，**预览与编辑器内容一致**
- PPT 风格素材面板（文本框 / 矩形 / 表格 / 图标 / 图片 / 图表）与页面背景色
- **版式叠加**：素材面板版式（含「更多版式」）点击后**追加**到当前画布，不替换整页；**新建页面默认为空白页**，需要版式时从素材面板叠加或套用
- **自定义版式（管理端）**：`/admin/layouts` 增删改查；粘贴 `canvas_elements` JSON，启用后出现在素材面板
- **组件层级**：页面背景最底；画布工具栏支持置顶 / 置底 / 上移一层 / 下移一层
- Word 风格文本格式工具栏
- **画布多选**：Ctrl / Shift + 点击多选；拖动可移动整组；**Ctrl+C / Ctrl+V** 复制粘贴（F1 查看快捷键）
- **三栏编辑器**：左侧工具箱（页面 / 音乐 / 动效 / 素材，2×2 Tab）+ 中间画布 + 右侧 AI 面板
- AI 全量生成演示结构（模板：全量生成）
- AI 单页改写（模板：单页改写）
- **AI 配图生成**：先生成**原图预览**，再自选「适应宽度 / 填充页面 / 原始尺寸」添加到画布；选中图片后画布工具栏可切换适应方式
- 表格双击单元格编辑
- 分享链接 `/s/{slug}`
- **管理员控制台**：访问统计、订单仪表盘、用户管理、**版式管理**、**H5 模板编辑/PPT 导入**、在线编辑 `.env`
- Docker 一键本地/云端部署

完整需求追踪见 [`docs/需求清单.md`](docs/需求清单.md)。

## 部署文档

| 文档 | 说明 |
|------|------|
| [**docs/Push与发布规范.md**](docs/Push与发布规范.md) | **push 前检查清单**、分支约定、发布到 EC2（每次 push 必遵） |
| [`docs/部署说明.md`](docs/部署说明.md) | 本机 Docker、**AWS EC2 公网部署**、分享链接、Nginx、常见问题 |
| [`docs/CI-CD与分支策略.md`](docs/CI-CD与分支策略.md) | GitHub Actions CI/CD、`develop`/`main` 分支、Secrets、手动发布到 EC2 |
| [`docs/DockerHub连接失败.md`](docs/DockerHub连接失败.md) | 国内 Docker 镜像加速 |

**推荐流程：** 本机 / `develop` 日常开发 → 遵守 [Push与发布规范](docs/Push与发布规范.md) → CI 自动 build → 稳定后 merge `main` → GitHub Actions **手动 Deploy to EC2**。

### 规划中（P1）→ 已实现

对标易企秀互动组件（详见 [`docs/互动组件-对话生成器与文字云.md`](docs/互动组件-对话生成器与文字云.md)）：

| 组件 | 要点 |
|------|------|
| **对话生成器** | 固定三栏（预设 / 预览 / 设置）；窄屏等比缩放手机预览；**点击 / 自动播放**；逐句间隔可自由输入（100～60000 ms） |
| **文字云** | 手动关键词 + 粘贴表格 + CSV/xlsx 导入；6 种形状；插入矢量或图片 |

编辑器入口：工具箱 → **素材** → 互动组件。依赖：`html2canvas`、`wordcloud`、`xlsx`（`npm install`）。

## 快速开始（Docker）

1. 复制环境变量：

```bash
cp .env.example .env
# 编辑 .env，至少配置 LLM_RELAY_* 或 LLM_OFFICIAL_*
```

2. 构建并启动：

```bash
docker compose up -d --build
```

**国内若无法连接 Docker Hub**，改用：

```bash
docker compose -f docker-compose.yml -f docker-compose.cn.yml up -d --build
```

或本地启动：`.\scripts\start-local.ps1`（见 `docs/DockerHub连接失败.md`）

3. 浏览器打开：http://localhost:8080

## 本地开发（可选）

需 Node.js 20+、Python 3.12+（或通过 Docker 仅构建镜像）。

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# 前端（另开终端）
cd frontend
npm install
npm run dev
```

## 大模型档位与模型

| 档位 | 文稿生成 | AI 配图 |
|------|----------|---------|
| **免费（默认）** | `LLM_MODEL_FREE`（如 `gemini-3.1-flash-image-preview`） | `LLM_IMAGE_MODEL_FREE` |
| **升级** | `LLM_MODEL_PRO`（如 `gemini-3-pro-image-preview`） | `LLM_IMAGE_MODEL_PRO` |

可在 `.env` 中配置 `LLM_RELAY_BASE_URL`、`LLM_RELAY_API_KEY` 及上述模型名。**AI 智能面板仅在编辑器**（`/editor/:id`）右侧显示；探索模板主页只做模板浏览与筛选。

### 配图环境变量示例

```env
LLM_DEFAULT_CHANNEL=auto
LLM_AUTO_ORDER=relay,official
LLM_RELAY_BASE_URL=https://你的中转地址
LLM_RELAY_API_KEY=sk-...
LLM_IMAGE_MODEL_FREE=gemini-3.1-flash-image-preview
LLM_IMAGE_MODEL_PRO=gemini-3-pro-image-preview
```

### 编辑器 AI 配图

1. 右侧 **AI 助手** → 填写画面描述 → **AI 生图**
2. 在 **原图预览** 下方选择添加到页面的方式：**适应宽度** / **填充页面** / **原始尺寸**
3. 点击 **按当前方式添加**；已添加的图片可在画布上选中，顶部工具栏点 **适应宽 / 填充 / 原图** 切换

配置 `LLM_RELAY_*` 或 `LLM_OFFICIAL_*` 及 `LLM_IMAGE_MODEL_*`（见上文配图环境变量）。

### 编辑器快捷键（画布）

| 操作 | 快捷键 |
|------|--------|
| 多选（切换） | Ctrl + 点击 |
| 多选（追加） | Shift + 点击 |
| 复制 / 粘贴 | Ctrl+C / Ctrl+V |
| 删除选中 | Delete |
| 撤回 / 重做 | Ctrl+Z / Ctrl+Y |
| 层级调节 | 选中组件后工具栏：置顶 / 置底 / 上移 / 下移 |
| 帮助 | F1 或 Ctrl+/ |

小屏（宽度 &lt; 1280px）下工具箱与 AI 面板收为底部抽屉，避免三栏挤压画布。

### 探索模板 API

| 参数 | 说明 |
|------|------|
| `category` | 模板类型：全部 / 简约商务 / 叙事公益 / 对话故事 / 年度报告 / 产品发布 / … |
| `device` | 终端：`全部` / `mobile`（移动端）/ `web`（网页版） |
| `q` | 关键词（支持「移动端」「网页版」等） |

有完整 `slides_json` 的模板显示「可试看」，套用后可直接改字出片。

### 简约模板体系

双主题 + 版式块 + JSON 模板，参照 **zjy.pptx**（商务简约）与 **易企秀 5P8N3mJ7**（叙事 H5）。

| 主题 ID | 风格 | 典型模板 |
|---------|------|----------|
| `zjy-minimal` | 白底、青蓝 `#156082`、商务汇报 | `minimal-zjy-mobile/web` |
| `eqxiu-story` | 暖色叙事、纵向滑动 | `story-volunteer-mobile/web` |

**模板 JSON 位置**：`backend/data/h5_templates/`（启动时全量 sync 至 SQLite）

| 模板 ID | 页数 | 说明 |
|---------|------|------|
| `minimal-zjy-mobile` / `web` | 9 | ZJY 简约商务 |
| `story-volunteer-mobile` / `web` | 10 | 志愿叙事（易企秀结构） |
| `tech-launch-mobile` / `web` | 8 | 产品发布 |
| `corp-intro-mobile` / `web` | 8 | 企业介绍 |
| `story-wechat-mobile` / `v2` | 6~8 | 微信对话演示 |

**重新生成模板 JSON**（修改版式块或文案种子后）：

```bash
node scripts/generate-h5-templates.mjs
```

**编辑器用法**：

- 素材面板 → **版式**（标题 / 章节页 / 三要点 / 表格 / 更多版式）**叠加添加**到当前页；不改变已有页面背景
- 新建页面 → **默认空白页**；需要版式时从 **素材 → 版式** 叠加添加
- 选中画布组件 → 工具栏调节**层级**（置顶 / 置底 / 上移 / 下移）
- 动效面板 → 浏览模式、页动效
- **音乐** Tab → 启用 BGM、选择 `backend/static/bgm` 曲目；幻灯片内右上角旋转播放器

**管理端版式**（`/admin/layouts`）：

- 新建版式 → 填写名称、图标、分组与展示位置（主屏 / 更多版式）
- 粘贴手机端（及可选网页端）`canvas_elements` JSON → 启用
- 用户在编辑器 **素材 → 版式** 中即可叠加使用

**视觉规范文档**：

- [`docs/reference-frames/zjy-style-guide.md`](docs/reference-frames/zjy-style-guide.md)
- [`docs/reference-frames/eqxiu-volunteer-story.md`](docs/reference-frames/eqxiu-volunteer-story.md)

### 背景音乐（BGM）

| 项 | 说明 |
|----|------|
| 音频目录 | **`backend/static/bgm/`**（将 MP3 放入此目录） |
| 访问路径 | `/static/bgm/xxx.mp3` |
| 曲目 API | `GET /api/v1/bgm/曲目`（扫描 `static/bgm` 下 `*.mp3`） |
| 编辑器配置 | 工具箱 → **音乐** → 点击「启用背景音乐」→ 选择曲目 |
| 播放控制 | 幻灯片画框内右上角 **旋转唱片按钮**：播放时旋转，点击静音/继续；预览与分享同步 |
| 安装测试曲 | `.\scripts\install-bgm.ps1`（会写入 `static/bgm/`） |

曲目元数据（可选）：`backend/data/bgm_catalog.json`（用于自定义标题；未收录的文件名会自动出现在列表中）

## 大模型 auto 模式

设置 `LLM_DEFAULT_CHANNEL=auto` 后，按 `LLM_AUTO_ORDER` 依次尝试**已配置**的通道，并使用对应档位的 Gemini 模型名。

## 目录结构

```
develop/
├── backend/          # FastAPI
│   ├── app/
│   ├── data/
│   │   ├── h5_templates/   # H5 模板 JSON（启动 sync）
│   │   └── bgm_catalog.json
│   ├── media/bgm/          # 历史兼容目录（曲目列表以 static/bgm 为准）
│   ├── static/bgm/         # 背景音乐 MP3（推荐，勿提交二进制）
│   └── services/llm/image_provider.py
├── frontend/         # Vue 3 + Vite + Tailwind
│   └── src/constants/
│       ├── designThemes.js   # zjy-minimal / eqxiu-story
│       ├── layoutBlocks.js   # 14 种内置版式 + 自定义版式解析
│       └── templateSeeds.js  # 模板生成种子
├── scripts/
│   ├── generate-h5-templates.mjs
│   └── install-bgm.ps1
├── Dockerfile
├── docker-compose.yml
├── .cursor/rules/
│   ├── git-and-docs.mdc               # 每次 push 前检查（alwaysApply）
│   ├── deploy-release.mdc             # 部署/workflow 不变量
│   └── backend-engineering.mdc
├── .github/workflows/
│   ├── ci.yml                         # push develop/main：docker build 校验
│   └── deploy-ec2.yml                 # 手动 SSH 部署 EC2（跟踪 main）
└── docs/
    ├── 需求清单.md                    # 功能需求与完成状态（含 DG/WC、TM-07~15）
    ├── 互动组件-对话生成器与文字云.md    # P1 互动组件设计与验收
    ├── CI-CD与分支策略.md              # GitHub Actions、Secrets、分支发布
    ├── Push与发布规范.md               # push 前检查清单、发布流程（固定规范）
    ├── reference-frames/              # 视觉参照与截帧说明
    ├── Stitch原型对照.md
    └── 部署说明.md                    # 本地 Docker + EC2 + 分享链接
```

## 环境安装目录

后续如需在本机安装额外工具，统一放在 `E:\devolop\`，见该目录下 `已安装软件清单.md`。
