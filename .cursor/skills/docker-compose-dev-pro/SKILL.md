---
name: docker-compose-dev-pro
description: Docker 容器开发工具链。用 docker-compose 管理前端、后端、数据库等；代码在容器外编辑、容器内热更新；数据卷统一挂载到项目 data 目录；区分 dev 开发编排与 pro 生产编排。Use when working with Docker, docker-compose, container development, hot reload, dev vs production compose, or mounting volumes to project data.
---

# Docker Compose 开发与生产编排

## 核心约定

1. **数据卷统一挂载到项目 `data` 目录**  
   所有需要持久化的数据（数据库、包缓存、上传文件等）一律使用 `./data/<服务或用途>`，不在项目根目录散落其他卷路径。便于备份、迁移和 .gitignore 统一忽略 `data/`。

2. **开发 / 生产分离**  
   - **开发**：`docker-compose.yml` 或 `docker-compose.dev.yml`，面向本地开发，支持热更新。  
   - **生产**：`docker-compose.prod.yml`，面向部署，不挂载源码，仅用镜像 + 数据卷。

3. **开发环境“容器外改代码、容器内热更新”**  
   源码通过 bind mount 挂进容器（如 `./frontend:/app`、`./server:/app`），不把代码打进镜像。本地用编辑器改代码，容器内进程监听文件变化自动重载（如 Vite HMR、Flask debug、nodemon 等）。

---

## 数据卷规范

| 用途           | 挂载路径（宿主机） | 容器内路径示例           |
|----------------|--------------------|--------------------------|
| 数据库数据     | `./data/mysql`     | `/var/lib/mysql`         |
| 后端依赖缓存   | `./data/backend_packages` | `site-packages` 或 `/usr/local/lib/python3.x/site-packages` |
| 前端 node_modules 持久化（可选） | `./data/frontend_node_modules` | `/app/node_modules` |
| 上传/静态文件  | `./data/uploads`   | 应用内上传目录           |
| 其他持久化     | `./data/<服务名或用途>` | 按需                     |

确保项目根目录有 `data/`，并在 `.gitignore` 中忽略（或只提交 `data/.gitkeep`）。

---

## 开发编排（dev）

- **文件名**：`docker-compose.yml` 或 `docker-compose.dev.yml`（若同时存在 pro，则 dev 用 `.dev.yml` 更清晰）。
- **启动**：`docker-compose up` 或 `docker-compose -f docker-compose.dev.yml up`。

要点：

- **数据库**：镜像 + 数据卷 `./data/mysql`，带 healthcheck；端口可按需映射便于本地客户端连接。
- **后端**：  
  - 使用官方语言镜像（如 `python:3.x`、`node:xx-alpine`），不强制多阶段构建。  
  - 源码挂载：`./server:/app`（或你的后端目录）。  
  - 依赖持久化（可选）：如 Python 把 `./data/backend_packages` 挂到 `site-packages`，避免每次启动重装。  
  - entrypoint/command 里：安装依赖 + 启动开发服务器（如 `flask run --host=0.0.0.0`、`uvicorn --reload`、`npm run dev`），保证改代码即热更新。
- **前端**：  
  - 源码挂载：`./frontend:/app`。  
  - 使用 dev server（如 Vite `pnpm dev --host 0.0.0.0`），实现 HMR。  
  - 如需持久化 node_modules 可挂载 `./data/frontend_node_modules:/app/node_modules`（注意与 package 管理器一致）。
- **开发辅助**：phpMyAdmin、Redis 等仅放在 dev 编排中，不放入 pro。

示例结构（仅示意）：

```yaml
# docker-compose.dev.yml
services:
  mysql:
    image: mysql:8.0
    volumes:
      - ./data/mysql:/var/lib/mysql
    # ... environment, healthcheck, ports

  backend:
    image: python:3.13
    volumes:
      - ./server:/app
      - ./data/backend_packages:/usr/local/lib/python3.13/site-packages
    # entrypoint: 安装依赖 + flask run / uvicorn --reload

  frontend:
    image: node:18-alpine
    volumes:
      - ./frontend:/app
    # entrypoint: pnpm install && pnpm dev --host 0.0.0.0
```

---

## 生产编排（pro）

- **文件名**：`docker-compose.prod.yml`。
- **启动**：`docker-compose -f docker-compose.prod.yml up -d`。

要点：

- **不挂载源码**：前端、后端均用构建好的镜像（本地 build 或从 registry 拉取）。
- **仅持久化数据**：数据库、上传目录、缓存等继续用 `./data/...`。
- **后端**：Dockerfile 中 COPY 代码、安装依赖、指定生产命令（如 gunicorn、uvicorn 无 `--reload`）。
- **前端**：Dockerfile 多阶段构建：build 阶段 `npm run build`，运行阶段用 nginx 或静态 server 托管 `dist`；或使用 node 镜像运行 `node server.js` 等。
- **环境变量**：通过 `env_file` 或 environment 注入，不把密钥写在 compose 里；可配合 `.env.prod` 与 `.gitignore`。

示例结构（仅示意）：

```yaml
# docker-compose.prod.yml
services:
  mysql:
    image: mysql:8.0
    volumes:
      - ./data/mysql:/var/lib/mysql
    # ... 同 dev，可收紧 ports

  backend:
    build: ./server
    # 或 image: my-registry/backend:latest
    volumes:
      - ./data/uploads:/app/uploads
    # 无源码挂载

  frontend:
    build: ./frontend
    volumes:
      - ./data/frontend_static:/app/dist
    # 或仅 nginx 读静态资源
```

---

## 常用命令速查

- 开发：`docker-compose up` 或 `docker-compose -f docker-compose.dev.yml up`（前台，看日志）。  
- 生产：`docker-compose -f docker-compose.prod.yml up -d`。  
- 重建并启动：`docker-compose up -d --build`（pro 同理加 `-f docker-compose.prod.yml`）。  
- 只看某服务：`docker-compose up mysql backend`。  
- 进入容器：`docker-compose exec backend bash`。

---

## 与用户沟通时的表述

- 用“开发编排 / 生产编排”“数据都放在项目的 data 目录里”等业务化说法，避免只说“volume”“bind mount”等术语；必要时再补充技术细节。
- 强调“在本地改代码，保存后容器里会自动更新，无需重建镜像”，降低环境依赖心智负担。
