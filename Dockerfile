# 构建参数：无法访问 Docker Hub 时，在 compose 中指定国内镜像前缀
ARG NODE_IMAGE=node:20-alpine
ARG PYTHON_IMAGE=python:3.12-slim
ARG NPM_REGISTRY=https://registry.npmmirror.com
# 国内可设清华/阿里；构建失败时会自动回退到其他源
ARG PIP_INDEX=https://pypi.org/simple

# 阶段 1：构建前端
FROM ${NODE_IMAGE} AS web-build
ARG NPM_REGISTRY=https://registry.npmmirror.com
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm config set registry "${NPM_REGISTRY}" \
    && npm install
COPY frontend/ ./
RUN npm run build

# 阶段 2：后端运行
FROM ${PYTHON_IMAGE}
ARG PIP_INDEX=https://pypi.org/simple
WORKDIR /app

ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PIP_DEFAULT_TIMEOUT=180 \
    PIP_RETRIES=8

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libffi-dev fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && set -eux; \
    pip_install() { \
      idx="$1"; host="$(echo "$idx" | sed -E 's|https?://([^/]+).*|\1|')"; \
      pip install --no-cache-dir --default-timeout=180 \
        -i "$idx" --trusted-host "$host" \
        -r backend/requirements.txt; \
    }; \
    pip_install "${PIP_INDEX}" \
      || pip_install "https://mirrors.aliyun.com/pypi/simple/" \
      || pip_install "https://pypi.tuna.tsinghua.edu.cn/simple" \
      || pip_install "https://pypi.org/simple"; \
    apt-get purge -y gcc libffi-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ ./backend/
COPY ppt-master-main/skills ./ppt-master-main/skills
COPY --from=web-build /app/backend/static ./backend/static

ENV PPT_MASTER_ROOT=/app/ppt-master-main \
    PPT_MASTER_WORKSPACE=/app/backend/data/ppt_master_projects \
    PPT_MASTER_MAX_CONCURRENT=1 \
    PPT_MASTER_SKIP_IMAGES=1

WORKDIR /app/backend
RUN mkdir -p /app/backend/data

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
