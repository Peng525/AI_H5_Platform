# EC2 Docker 完整部署计划

> 与 Cursor Plan **EC2 Docker 部署** 同步。完整可勾选 todos 见 Cursor Plans 面板。

## 环境约定

| 项 | 值 |
|----|-----|
| SSH 用户 | `ec2-user` |
| 访问 | 公有 DNS `:8080` |
| 路径 | `/home/ec2-user/AI_H5_Platform` |
| 分支 | `main`（开发用 `develop`） |

详细步骤见 [部署说明.md](./部署说明.md) 与 [CI-CD与分支策略.md](./CI-CD与分支策略.md)。

## 执行顺序

1. 安全组 22 + 8080
2. `ssh ec2-user@<DNS>`
3. 装 Docker + compose
4. `git clone` + `checkout main`
5. `cp .env.example .env` 并编辑
6. `docker compose up -d --build`
7. 浏览器 `http://<DNS>:8080`
8. DNS 下发布验证分享链接
9. GitHub Secrets + 手动 Deploy
