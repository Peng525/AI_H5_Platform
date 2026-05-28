# Docker Hub 连接失败（auth.docker.io 超时）

## 错误特征

```
failed to fetch oauth token: Post "https://auth.docker.io/token"
dial tcp [2a03:2880:...]:443: connectex: ... failed to respond
```

常见原因：国内网络无法稳定访问 Docker Hub、或 Docker 走了 IPv6 但链路不通。

---

## 方案 A：使用国内镜像构建（推荐，改一条命令）

在项目 `develop` 目录执行：

```powershell
docker compose -f docker-compose.yml -f docker-compose.cn.yml up -d --build
```

会通过 `docker.m.daocloud.io` 拉取 `node` / `python` 基础镜像，并用 npmmirror / 清华 pip 加速依赖。

若 DaoCloud 也失败，可编辑 `docker-compose.cn.yml`，将镜像改为阿里云个人加速器地址（需登录阿里云容器镜像服务获取专属 URL）。

---

## 方案 B：配置 Docker Desktop 镜像加速

1. 打开 **Docker Desktop → Settings → Docker Engine**
2. 在 JSON 中加入（保留原有字段，合并 `registry-mirrors`）：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io"
  ],
  "ipv6": false
}
```

3. **Apply & Restart**
4. 再执行：

```powershell
docker compose up -d --build
```

> 公共镜像站可能变动，请以当前可用的国内镜像文档为准；企业环境建议使用阿里云/腾讯云**专属**加速地址。

---

## 方案 C：关闭 IPv6（针对日志里出现 `2a03:2880`）

在 Docker Engine JSON 中设置 `"ipv6": false` 后重启 Docker（见方案 B）。

或在 Windows 网络适配器中暂时禁用 IPv6 后重试构建。

---

## 方案 D：不用 Docker，本地直接运行

已安装 **Node.js 20+** 与 **Python 3.12+** 时：

```powershell
cd "E:\cursor projects\类ppt 小程序\develop"
.\scripts\start-local.ps1
```

浏览器访问 http://localhost:8080

---

## 方案 E：使用代理

若本机有 HTTP/HTTPS 代理，在 Docker Desktop → Resources → Proxies 中填写后重启，再执行 `docker compose up -d --build`。
