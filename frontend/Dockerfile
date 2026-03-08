# 开发环境前端镜像：预装 pnpm，使用国内源，启动时挂载源码实现热更新
FROM node:20.18-alpine3.19

# 使用国内镜像源（Alpine 阿里云）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 使用 npm 安装 pnpm（避免 corepack 签名校验 keyid 不匹配问题），并配置国内镜像
RUN npm config set registry https://registry.npmmirror.com \
    && npm install -g pnpm \
    && pnpm config set registry https://registry.npmmirror.com

WORKDIR /app

# 启动时由 entrypoint 执行 pnpm install + pnpm dev
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
