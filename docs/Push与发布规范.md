# Push 与发布规范

本文是仓库 **push / 合并 / 上云** 的固定流程。Agent 与开发者每次 push 前须遵守；细则见 [部署说明.md](./部署说明.md)、[CI-CD与分支策略.md](./CI-CD与分支策略.md)。

---

## 1. 分支与职责（固定）

| 分支 | 用途 | push 后 | 是否上 EC2 |
|------|------|---------|------------|
| `develop` | 日常开发、联调 | CI 自动 `docker build` | **否** |
| `main` | 对外 MVP / 稳定演示 | CI 自动 `docker build` | **仅手动** Deploy workflow |

**禁止：** 在 `develop` 上直接改 EC2 生产数据预期；**禁止** 把 `.env`、API Key、`.pem` 提交进 Git。

---

## 2. Push 前检查清单（必做）

每次 `git push` 前逐项确认：

### 2.1 安全

- [ ] `git status` 中**无** `.env`、密钥、`.pem`、`data/app.db` 等敏感文件
- [ ] 新增环境变量已写入 `.env.example`（若有），**未**写入真实密钥值
- [ ]  diff 中无硬编码 API Key / JWT / 密码

### 2.2 代码与构建

- [ ] **开发完毕**已在项目根目录执行 `docker build -t ai-h5-platform:local .` 且**成功**（与 CI 一致）
- [ ] 构建失败已修复并重新 build 通过，再 push
- [ ] 国内可改用 `docker compose -f docker-compose.yml -f docker-compose.cn.yml build`

### 2.3 文档（按影响范围）

| 变更类型 | 至少更新 |
|----------|----------|
| 新功能 / API / 路由 | `docs/需求清单.md` + `README.md` |
| 环境变量 | `.env.example` + `docs/部署说明.md` |
| 部署 / CI/CD / 分支 | 本文 + `docs/CI-CD与分支策略.md` + `docs/部署说明.md` |
| 小修复（ typo、单行样式） | 可只 push，不必改文档 |

### 2.4 Git 操作

- [ ] 当前分支正确：日常开发 → `develop`；**不要** 未经确认 force push `main`
- [ ] Commit message 与仓库风格一致：`feat:` / `fix:` / `docs:` / `chore:`
- [ ] 默认推送：`git push origin develop`（或当前功能分支）

### 2.5 与上线的关系（易错）

- [ ] **Push `develop` ≠ 更新 EC2**；朋友看到的线上版本只在手动 Deploy 后变化
- [ ] 需要更新云上 MVP：merge `main` → GitHub Actions → **Deploy to EC2**（见下文 §4）

---

## 3. 标准开发 Push 流程

```
改代码 → docker build 成功 → 文档（若需要）→ commit → push develop → 等 CI 绿勾
```

1. 在项目根目录（含 `Dockerfile`）开发
2. **开发完毕**：执行 `docker build -t ai-h5-platform:local .`，失败则修复至成功
3. 执行 §2 检查清单
4. `git add` → `git commit -m "feat: ..."` → `git push origin develop`
5. 打开 GitHub Actions → **CI** 工作流通过后再考虑合并 `main`

---

## 4. 发布到 EC2（与 push 分离）

**仅在需要更新对外演示环境时执行：**

1. `develop` 自测 + CI 通过
2. PR：`develop` → `main`，审查后合并
3. GitHub → **Actions** → **Deploy to EC2** → **Run workflow**（默认分支 `main`）
4. 用 `http://<EC2_DNS或域名>:8080` 访问并**重新发布**分享页（分享链接依赖 `origin`）

Deploy 工作流（[`.github/workflows/deploy-ec2.yml`](../.github/workflows/deploy-ec2.yml)）会：

- SSH 到 EC2（凭证来自 GitHub Secrets：`EC2_HOST`、`EC2_USER`、`EC2_SSH_KEY`）
- `git pull origin main` + `docker compose up -d --build`
- **不覆盖** 服务器上 `.env` 与 `./data`

业务密钥只存在于 **EC2 本机 `.env`**，不在 GitHub Secrets（除 SSH 部署凭证外）。

---

## 5. Secrets 存放（固定）

| 位置 | 内容 |
|------|------|
| GitHub Secrets | `EC2_HOST`、`EC2_USER`、`EC2_SSH_KEY`、可选 `EC2_APP_PATH` |
| EC2 `~/AI_H5_Platform/.env` | `JWT_SECRET`、LLM Key、验证码等（Amazon Linux 用户目录为 `/home/ec2-user/`） |
| 切勿提交 Git | `.env`、`.pem`、`data/` 内数据库 |

**本仓库 EC2 推荐配置示例：**

| Secret | 值 |
|--------|-----|
| `EC2_HOST` | EC2 公有 DNS（如 `ec2-xx-xx-xx.ap-northeast-1.compute.amazonaws.com`） |
| `EC2_USER` | `ec2-user` |
| `EC2_APP_PATH` | `/home/ec2-user/AI_H5_Platform`（未设置时 Deploy workflow 使用此默认） |

---

## 6. Commit 与 Push 约定

| 项 | 约定 |
|----|------|
| 作者 | `Peng525` / `11327@users.noreply.github.com`（不修改 git config） |
| 默认远程分支 | `origin develop` |
| 创建 commit | **仅**在用户明确要求时执行 |
| Force push | 禁止对 `main`，除非用户明确要求 |

---

## 7. Push 失败处理

1. 检查网络与 `git remote -v`
2. 若有冲突：先 `git pull --rebase origin <branch>` 再 push
3. CI 失败：本地 `docker build -t ai-h5-platform:local .` 复现并修复后重新 build，再 push
4. 向用户说明失败原因与已做处理

---

## 8. 相关文档索引

| 文档 | 用途 |
|------|------|
| [部署说明.md](./部署说明.md) | Docker、EC2 首次安装、分享链接、Nginx |
| [CI-CD与分支策略.md](./CI-CD与分支策略.md) | Actions 详解、Secrets、回滚 |
| [DockerHub连接失败.md](./DockerHub连接失败.md) | 国内镜像加速 |
| [`.cursor/rules/git-and-docs.mdc`](../.cursor/rules/git-and-docs.mdc) | Agent 每次 push 前执行的规则 |
