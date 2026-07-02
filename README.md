# AI 智能 H5 平台

的 AI 驱动 H5 演示生成与播放平台，同时支持简历编辑和简历优化。全简体中文界面，支持 **auto / 中转 API / 官方 API** 三种大模型通道，内置PPT **全量生成** 与 **单页改写** 两套提示词模板。

## 快速开始

1. 克隆仓库，在项目根目录（含 `Dockerfile`、`docker-compose.yml`）执行：

```bash
cp .env.example .env
# 编辑 .env：至少配置 JWT_SECRET、ADMIN_USERNAMES（你的管理员邮箱）
# 使用 AI 功能时配置 LLM_RELAY_* 或 LLM_OFFICIAL_*
docker compose up -d --build
```

2. 浏览器打开 **http://localhost:8080**（若 Windows 提示 8080 端口无法绑定，见下方「本机端口冲突」）

3. 使用**邮箱注册/登录**；管理员可在用户管理页授予，或 `.env` 的 `ADMIN_USERNAMES` 配置邮箱（兜底）

**Windows 若 8080 无法绑定（Hyper-V 保留端口，无进程可 kill）：** 以管理员打开 PowerShell，在 `develop` 目录执行：

```powershell
.\scripts\setup-host-port-8080.ps1
```

成功后访问 **http://localhost:8080**

**国内 Docker Hub 较慢时：**

```bash
docker compose -f docker-compose.yml -f docker-compose.cn.yml up -d --build
```

详见 [`docs/DockerHub连接失败.md`](docs/DockerHub连接失败.md)。

> 账号与密码由你自行设定，保存在本机 `.env` 与数据库中，**勿将 `.env` 提交到 Git**。

## 功能概览

- 项目管理、页面编辑、全屏 H5 预览与分享链接 `/s/{slug}`
- **项目 URL 标识**：编辑器/预览/发布/生成结果等路由使用 opaque `public_id`（NanoID），不暴露数据库自增 id；旧数字 URL 自动重定向
- **AI 生成向导**（登录默认）：Gamma 两态单页（deck 示例 / image 三胶囊+生图模板 → 有输入「编辑提示词」）→ 演示文稿进提示编辑器 → **生成结果页**（紧凑卡片纵览、选中组件时浮层格式工具栏、内联编辑；添加素材走右侧栏）；图片类型进两栏生图页
- **我的工作台**：双栏侧栏显示用户名；**首页**为项目列表、**模板库**可选模板；顶栏 **新建演示** 与 **导入 PPT**
- **模板库**：按类型与终端筛选；封面渲染第一页缩略图
- **简约模板体系**：商务 + 叙事双主题，多种版式与 JSON 模板
- **背景音乐**：`backend/static/bgm/` 放置 MP3，编辑器内选曲播放
- **版式叠加**：素材面板版式追加到画布；**新建页面默认为空白页**
- **自定义版式**（管理端 `/admin/layouts`）
- **组件层级**：置顶 / 置底 / 上移 / 下移
- **画布多选**、复制粘贴、撤回重做（Studio 编辑器工具栏或 Ctrl+Z/Y；结果页无顶栏撤销/添加，F1 查看快捷键）
- **三栏编辑器**：工具箱 + 画布 + AI 面板
- **互动组件**：对话生成器、文字云、**图表卡组**（素材 → 特殊组件；多图堆叠上下切换，后大前小景深；编辑器内嵌拖拽条）
- **管理员控制台**（`/admin`）：数据仪表盘（访问统计、订单、近 14 日趋势图）、待支付订单确认、用户/模板/版式/提示词管理；**中转 API 充值**仅提供外链（推理令牌无法自动读余额）
- **使用帮助**：登录后用户菜单 → `/help`（FAQ、快捷键）

## 配置说明

复制 `.env.example` 为 `.env`。常用项：

| 变量 | 说明 |
|------|------|
| `JWT_SECRET` | 登录令牌密钥（随机长字符串） |
| `ADMIN_USERNAMES` | 管理员邮箱（逗号分隔，启动时同步至 `users.is_admin`，兜底授权） |
| `CAPTCHA_PROVIDER` | `mock`（开发）或 `tencent`（上线推荐） |
| `LLM_RELAY_*` / `LLM_OFFICIAL_*` | AI 文稿与配图通道 |
| `RELAY_DASHBOARD_RECHARGE_URL` | 管理端「前往中转平台钱包」链接（可选；NovAI 示例见下） |

配图与中继示例：

```env
LLM_DEFAULT_CHANNEL=auto
LLM_RELAY_BASE_URL=https://你的中转地址/v1
LLM_RELAY_API_KEY=你的推理令牌
# 管理端充值外链（余额需登录中转站控制台自行查看）
RELAY_DASHBOARD_RECHARGE_URL=https://once-cf.novai.su/wallet
```

> **说明：** `LLM_RELAY_API_KEY` 仅用于调用大模型接口；多数中转站的推理令牌**不能**查询账户余额，管理端不会自动显示余额，只提供上述充值链接。

## 管理员控制台

管理员可在 `/admin/users` 勾选「设为管理员」，或登录邮箱在 `.env` 的 `ADMIN_USERNAMES` 中；登录后自动进入 `/admin`。

| 页面 | 功能 |
|------|------|
| `/admin` | 今日/近 7 日访问、成交订单与成交额、近 14 日访问趋势图、待支付微信订单确认、近期订单列表、**中转 API 充值外链** |
| `/admin/users` | 创建用户、改会员档位、调整 API 配额、**UI 授予管理员** |
| `/admin/templates` | H5 探索模板 CRUD、可视化编辑（EditorStudio）、保存预设、PPTX 导入 |
| `/admin/layouts` | **14 内置版式 + 自定义**；点「编辑」进入 EditorStudio 可视化编辑，「保存版式」写回库 |
| `/admin/prompts` | 文稿提示词（Gamma 三栏布局：设置 / System·User / 说明） |
| `/admin/image-prompts` | 生图提示词模板 |
| `/settings` | 大模型通道与 `.env` 在线保存 |

**中转 API 充值：** 配置 `RELAY_DASHBOARD_RECHARGE_URL` 后，仪表盘显示「前往中转平台钱包」。余额须在中转站控制台用账号密码登录查看；`LLM_RELAY_API_KEY` 只负责调模型，不能代替网页登录查余额。

**H5 模板可视化编辑：** `/admin/templates` 点「编辑」进入三栏编辑器；顶栏仅显示「管理控制台」（无探索模板/我的项目）；小屏侧栏以抽屉打开。顶栏「**保存为预设**」（蓝底白字）写回探索模板库；「从 PPT 导入」可替换草稿内容。

**版式可视化编辑：** `/admin/layouts` 点「编辑」同样进入 EditorStudio（`?adminLayout=`）；顶栏「保存版式」将画布写回版式库，素材面板即时生效。

管理端侧栏已移除「返回用户端」；退出请用右上角用户菜单。右侧主内容区独立滚动，长页面无需滚到底部才能退出。

## 用户端路由

| 路由 | 说明 |
|------|------|
| `/create/generate` | **登录默认** — Gamma 两态单页（deck 示例 / image 比例·颜色·风格 + 生图模板 →「编辑提示词」） |
| `/create/generate/prompt` | 已合并至 generate（重定向） |
| `/create/generate/review` | 提示编辑器 → 全量生成 |
| `/create/generate/image` | 独立 AI 生图（返回首页；两栏编辑/结果；裁切、复制） |
| `/dashboard` | 工作台 · 首页（项目列表） |
| `/templates` | 工作台 · 模板库 |
| `/editor/:id` | 三栏编辑器 |
| `/preview/:id` | 全屏预览 |
| `/publish/:id` | 发布成功页 |
| `/upgrade` | 套餐升级 |
| `/help` | 使用帮助 |

向导详细说明见 [`docs/AI生成向导.md`](docs/AI生成向导.md)；**按钮交互与 LLM 映射**见 [`docs/功能开发说明书.md`](docs/功能开发说明书.md)；**生成页组件开发逻辑**见 [`docs/生成页组件与开发逻辑.md`](docs/生成页组件与开发逻辑.md)；**UI 测试用例**见 [`docs/生成页测试用例.md`](docs/生成页测试用例.md)。

### 外部生成 PPT（Cursor + PPT Master）

在本机用 Cursor 生成可编辑 `.pptx` 并导入探索模板，见 **[docs/AI-PPT生成指南.md](docs/AI-PPT生成指南.md)**（最终版入口，含五模型横评与 H5 导入步骤）。方案详表见 [docs/AI-PPT生成方案对比.md](docs/AI-PPT生成方案对比.md)。

---

## 编辑器要点

### AI 配图

1. 右侧 **AI 助手** → 选择 **生图分辨率**（苹果 / 安卓 / 网页固定尺寸，默认与当前画布一致）
2. 填写画面描述 → **AI 生图**（按所选分辨率内容区比例生成竖屏/横屏图）
3. **原图预览** 下方选择放置方式：
   - **适应宽度**：宽度贴齐画布，高度按比例
   - **填充页面**：铺满当前画布内容区，完整显示不裁切
   - **原始尺寸**：等比缩放，框紧包裹图片
4. 点击添加；已上图可在画布工具栏切换 **适应宽 / 填充 / 原图** 或 **裁切**（选中图片时不显示背景颜色选项）

### 快捷键（画布）

| 操作 | 快捷键 |
|------|--------|
| 多选 | Ctrl / Shift + 点击 |
| 复制 / 粘贴 | Ctrl+C / Ctrl+V |
| 撤回 / 重做 | Ctrl+Z / Ctrl+Y |
| 帮助 | F1 |

### 版式与 BGM

- **素材 → 版式**：叠加到当前页
- **工具箱 → 音乐**：启用 BGM，曲目来自 `backend/static/bgm/`

## 部署到服务器

自建或云上部署（含 AWS EC2、分享链接、HTTPS）见 **[`docs/部署说明.md`](docs/部署说明.md)**。

## 本地开发（可选）

需 Node.js 20+、Python 3.12+，或直接仅用 Docker 构建。

```bash
# 后端
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# 前端（另开终端）
cd frontend && npm install && npm run dev
```

## 目录结构

```
├── backend/          # FastAPI API 与静态资源
├── frontend/         # Vue 3 编辑器与站点
├── data/             # SQLite 与运行时数据（Docker 挂载）
├── docs/             # 使用与部署文档
├── scripts/          # 辅助脚本
├── Dockerfile
└── docker-compose.yml
```

## 更多文档

| 文档 | 说明 |
|------|------|
| [`docs/部署说明.md`](docs/部署说明.md) | Docker、EC2、分享链接、Nginx |
| [`docs/Push与发布规范.md`](docs/Push与发布规范.md) | push 前检查、分支约定、EC2 发布 |
| [`docs/CI-CD与分支策略.md`](docs/CI-CD与分支策略.md) | GitHub Actions、分支与 Secrets |
| [`docs/AI生成向导.md`](docs/AI生成向导.md) | 三步向导、API、冒烟检查 |
| [`docs/功能开发说明书.md`](docs/功能开发说明书.md) | 各按钮逻辑、草稿字段、LLM 映射 |
| [`docs/互动组件-对话生成器与文字云.md`](docs/互动组件-对话生成器与文字云.md) | 对话生成器、文字云 |
| [`docs/互动组件-图表卡组.md`](docs/互动组件-图表卡组.md) | 图表卡组（堆叠卡片、上下切换） |
| [`docs/需求清单.md`](docs/需求清单.md) | 功能需求与完成状态 |
| 应用内 [`/help`](frontend/src/views/Help.vue) | 登录后用户菜单「使用帮助」 |

## 常见问题

| 问题 | 处理建议 |
|------|----------|
| AI 生图失败 | 检查 `.env` 中 `LLM_RELAY_*` 或 `LLM_OFFICIAL_*`；管理员在系统设置测试连通性 |
| AI 全量生成失败 | 同上；确认配额未用尽；查看 [`docs/AI生成向导.md`](docs/AI生成向导.md) |
| 管理端看不到中转余额 | 正常：推理令牌无法查余额；在 `/admin` 点击「前往中转平台钱包」登录控制台查看 |
| BGM 列表为空 | 将 MP3 放入 `backend/static/bgm/` 后重启服务 |
| 分享链接打不开 | 确认端口与安全组放行；项目需有有效 `share_slug` |
| 升级支付未到账 | 个人微信码需手动输入金额；等待轮询或联系管理员确认订单 |

登录后可在用户菜单打开 **使用帮助**（`/help`）查看详情。

## 许可证

使用与二次部署请遵守仓库许可及所用第三方 API 服务条款。
