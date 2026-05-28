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
| 功能 | 数据仪表盘、用户管理、订单查看、系统设置 |
| 说明 | 登录后自动进入 `/admin`；可创建用户、调整会员与 API 配额 |

普通用户导航栏不显示管理入口。

## 功能概览（P0）

- 项目管理、页面编辑、全屏 H5 预览
- **探索模板**：按模板类型 + 终端（移动端 / 网页版）筛选；主页不含 AI 面板
- PPT 风格素材面板（文本框 / 矩形 / 表格 / 图标 / 图片 / 图表）与页面背景色
- Word 风格文本格式工具栏
- AI 全量生成演示结构（模板：全量生成）
- AI 单页改写（模板：单页改写）
- **AI 配图生成**：读取 `.env` 通道与 `LLM_IMAGE_MODEL_*`，面板预览、复制、一键添加到画布（适应宽度 / 填充页面 / 原始尺寸）
- 表格双击单元格编辑
- 分享链接 `/s/{slug}`
- **管理员控制台**：访问统计、订单仪表盘、用户管理、在线编辑 `.env`
- Docker 一键本地/云端部署

完整需求追踪见 [`docs/需求清单.md`](docs/需求清单.md)。

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

编辑器 **「生成配图」** → `POST /api/v1/项目/{id}/生成/配图`；**「仅生成文案」** → 单页改写接口。

### 探索模板 API

| 参数 | 说明 |
|------|------|
| `category` | 模板类型：全部 / 年度报告 / 产品发布 / … |
| `device` | 终端：`全部` / `mobile`（移动端）/ `web`（网页版） |
| `q` | 关键词（支持「移动端」「网页版」等） |

## 大模型 auto 模式

设置 `LLM_DEFAULT_CHANNEL=auto` 后，按 `LLM_AUTO_ORDER` 依次尝试**已配置**的通道，并使用对应档位的 Gemini 模型名。

## 目录结构

```
develop/
├── backend/          # FastAPI
│   ├── app/
│   ├── services/llm/image_provider.py  # AI 配图（images/generations + chat modalities）
│   └── templates/    # 全量生成.yaml、单页改写.yaml
├── frontend/         # Vue 3 + Vite + Tailwind
├── Dockerfile
├── docker-compose.yml
└── docs/
    ├── 需求清单.md          # 功能需求与完成状态
    ├── Stitch原型对照.md
    └── 部署说明.md
```

## 环境安装目录

后续如需在本机安装额外工具，统一放在 `E:\devolop\`，见该目录下 `已安装软件清单.md`。
