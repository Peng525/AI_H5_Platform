# 构建参数：无法访问 Docker Hub 时，在 compose 中指定国内镜像前缀
ARG NODE_IMAGE=node:20-alpine
ARG PYTHON_IMAGE=python:3.12-slim
ARG NPM_REGISTRY=https://registry.npmmirror.com
ARG PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple

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
ARG PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /app

ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PIP_INDEX=${PIP_INDEX} \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        -i "${PIP_INDEX}" \
        --trusted-host pypi.tuna.tsinghua.edu.cn \
        -r backend/requirements.txt \
    && apt-get purge -y gcc libffi-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ ./backend/
COPY --from=web-build /app/backend/static ./backend/static

WORKDIR /app/backend
RUN mkdir -p /app/backend/data

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
