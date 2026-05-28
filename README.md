# AI 智能 H5 演示平台

类 PPT 的 AI 驱动 H5 演示生成与播放平台。全简体中文界面，支持 **auto / 中转 API / 官方 API** 三种大模型通道，内置 **全量生成** 与 **单页改写** 两套提示词模板。

- GitHub: [Peng525/AI_H5_Platform](https://github.com/Peng525/AI_H5_Platform)
- 开发分支: `develop`

## 功能概览（P0）

- 项目管理、页面编辑、全屏 H5 预览
- AI 全量生成演示结构（模板：全量生成）
- AI 单页改写（模板：单页改写）
- 分享链接 `/s/{slug}`
- 系统设置：大模型连通性测试
- Docker 一键本地/云端部署

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

| 档位 | 文稿生成 | 配图（免费配图同档） |
|------|----------|----------------------|
| **免费（默认）** | `gemini-3.1-flash` | `gemini-3.1-flash` |
| **升级** | `gemini-3-pro` | `gemini-3-pro` |

可在 `.env` 中通过 `LLM_MODEL_FREE`、`LLM_MODEL_PRO`、`LLM_IMAGE_MODEL_*` 覆盖。创建演示时可选档位；升级会员后请求传 `tier=pro`。

## 大模型 auto 模式

设置 `LLM_DEFAULT_CHANNEL=auto` 后，按 `LLM_AUTO_ORDER` 依次尝试**已配置**的通道，并使用对应档位的 Gemini 模型名。

## 目录结构

```
develop/
├── backend/          # FastAPI
│   ├── app/
│   └── templates/    # 全量生成.yaml、单页改写.yaml
├── frontend/         # Vue 3 + Vite + Tailwind
├── Dockerfile
├── docker-compose.yml
└── docs/
```

## 环境安装目录

后续如需在本机安装额外工具，统一放在 `E:\devolop\`，见该目录下 `已安装软件清单.md`。
