# 开发环境后端镜像：依赖预装，启动时仅挂载源码实现热更新
FROM python:3.13-slim

# 安装系统依赖（一次性，打进镜像）
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 预装 Python 依赖（避免每次启动重复安装）
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 阿里云 NLS SDK 通过 data/nls/*.whl 挂载，由 entrypoint 按需安装
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
