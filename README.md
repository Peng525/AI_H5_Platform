# AI 智能 H5 演示平台

类 PPT 的 AI 驱动 H5 演示生成与播放平台。全简体中文界面，支持 **auto / 中转 API / 官方 API** 三种大模型通道，内置 **全量生成** 与 **单页改写** 两套提示词模板。

## 快速开始

1. 克隆仓库，在项目根目录（含 `Dockerfile`、`docker-compose.yml`）执行：

```bash
cp .env.example .env
# 编辑 .env：至少配置 JWT_SECRET、ADMIN_USERNAMES（你的管理员邮箱）
# 使用 AI 功能时配置 LLM_RELAY_* 或 LLM_OFFICIAL_*
docker compose up -d --build
```

2. 浏览器打开 **http://localhost:8080**

3. 使用**邮箱注册/登录**；在 `.env` 的 `ADMIN_USERNAMES` 中配置的邮箱可进入管理控制台 `/admin`

**国内 Docker Hub 较慢时：**

```bash
docker compose -f docker-compose.yml -f docker-compose.cn.yml up -d --build
```

详见 [`docs/DockerHub连接失败.md`](docs/DockerHub连接失败.md)。

> 账号与密码由你自行设定，保存在本机 `.env` 与数据库中，**勿将 `.env` 提交到 Git**。

## 功能概览

- 项目管理、页面编辑、全屏 H5 预览与分享链接 `/s/{slug}`
- **探索模板**：按类型与终端筛选；封面渲染第一页缩略图
- **简约模板体系**：商务 + 叙事双主题，多种版式与 JSON 模板
- **背景音乐**：`backend/static/bgm/` 放置 MP3，编辑器内选曲播放
- **版式叠加**：素材面板版式追加到画布；**新建页面默认为空白页**
- **自定义版式**（管理端 `/admin/layouts`）
- **组件层级**：置顶 / 置底 / 上移 / 下移
- **画布多选**、复制粘贴、撤回重做（工具栏按钮或 Ctrl+Z/Y；F1 查看快捷键）
- **三栏编辑器**：工具箱 + 画布 + AI 面板
- **AI 全量生成 / 单页改写 / 配图**：生图前选分辨率，预览后自选适应宽度、填充页面或原始尺寸添加
- **互动组件**：对话生成器、文字云、**图表卡组**（素材 → 特殊组件；多图堆叠上下切换，后大前小景深；编辑器内嵌拖拽条）
- **管理员控制台**（`/admin`）：数据仪表盘（访问统计、订单、近 14 日趋势图）、待支付订单确认、用户/模板/版式/提示词管理；**中转 API 充值**仅提供外链（推理令牌无法自动读余额）
- **使用帮助**：登录后用户菜单 → `/help`（FAQ、快捷键）

## 配置说明

复制 `.env.example` 为 `.env`。常用项：

| 变量 | 说明 |
|------|------|
| `JWT_SECRET` | 登录令牌密钥（随机长字符串） |
| `ADMIN_USERNAMES` | 管理员邮箱，逗号分隔 |
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

登录邮箱须在 `.env` 的 `ADMIN_USERNAMES` 中；登录后自动进入 `/admin`。

| 页面 | 功能 |
|------|------|
| `/admin` | 今日/近 7 日访问、成交订单与成交额、近 14 日访问趋势图、待支付微信订单确认、近期订单列表、**中转 API 充值外链** |
| `/admin/users` | 创建用户、改会员档位、调整 API 配额 |
| `/admin/templates` | H5 探索模板 CRUD、可视化编辑（EditorStudio）、保存预设、PPTX 导入 |
| `/admin/layouts` | 素材版式块管理 |
| `/admin/prompts` | 文稿提示词（全量生成 / 单页改写） |
| `/admin/image-prompts` | 生图提示词模板 |
| `/settings` | 大模型通道与 `.env` 在线保存 |

**中转 API 充值：** 配置 `RELAY_DASHBOARD_RECHARGE_URL` 后，仪表盘显示「前往中转平台钱包」。余额须在中转站控制台用账号密码登录查看；`LLM_RELAY_API_KEY` 只负责调模型，不能代替网页登录查余额。

**H5 模板可视化编辑：** `/admin/templates` 点「编辑」进入与用户端相同的三栏编辑器（版式、音乐、素材、AI）；顶栏「保存为预设」写回探索模板库；「从 PPT 导入」可替换草稿内容。模板编辑草稿不会出现在「我的项目」列表。

侧栏「返回用户端 / 退出登录」固定于屏幕底部；右侧主内容区独立滚动，长页面无需滚到底部才能退出。

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
| [`docs/互动组件-对话生成器与文字云.md`](docs/互动组件-对话生成器与文字云.md) | 对话生成器、文字云 |
| [`docs/互动组件-图表卡组.md`](docs/互动组件-图表卡组.md) | 图表卡组（堆叠卡片、上下切换） |
| [`docs/需求清单.md`](docs/需求清单.md) | 功能需求与完成状态 |
| 应用内 [`/help`](frontend/src/views/Help.vue) | 登录后用户菜单「使用帮助」 |

## 常见问题

| 问题 | 处理建议 |
|------|----------|
| AI 生图失败 | 检查 `.env` 中 `LLM_RELAY_*` 或 `LLM_OFFICIAL_*`；管理员在系统设置测试连通性 |
| 管理端看不到中转余额 | 正常：推理令牌无法查余额；在 `/admin` 点击「前往中转平台钱包」登录控制台查看 |
| BGM 列表为空 | 将 MP3 放入 `backend/static/bgm/` 后重启服务 |
| 分享链接打不开 | 确认端口与安全组放行；项目需有有效 `share_slug` |
| 升级支付未到账 | 个人微信码需手动输入金额；等待轮询或联系管理员确认订单 |

登录后可在用户菜单打开 **使用帮助**（`/help`）查看详情。

## 许可证

使用与二次部署请遵守仓库许可及所用第三方 API 服务条款。
