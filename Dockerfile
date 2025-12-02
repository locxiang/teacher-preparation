# 多阶段构建：前端构建阶段
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./
COPY frontend/pnpm-lock.yaml* ./

# 安装前端依赖（优先使用 pnpm，如果没有则使用 npm）
RUN if [ -f pnpm-lock.yaml ]; then \
      npm install -g pnpm && pnpm install --frozen-lockfile; \
    else \
      npm ci; \
    fi

# 复制前端源代码
COPY frontend/ .

# 构建前端
RUN if [ -f pnpm-lock.yaml ]; then pnpm build; else npm run build; fi

# 后端运行阶段
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY server/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端应用代码
COPY server/ .

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建必要的目录
RUN mkdir -p uploads/audio

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["python", "app.py"]

