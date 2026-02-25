# 开发环境前端镜像：预装 pnpm，启动时挂载源码 + 持久化 node_modules 实现热更新
FROM node:20-alpine

# 启用 pnpm（Node 内置 corepack，无需 npm install -g）
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# 启动时由 entrypoint 执行 pnpm install + pnpm dev
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
