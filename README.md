# 教师备课会议系统

基于 Vue 3 + Flask 开发的智能教师备课会议系统，支持实时语音转写、AI 辅助对话和会议总结生成。

## 核心功能

- 🎤 **实时语音转写** - 支持阿里云通义听悟、科大讯飞 ASR，实时将语音转换为文字
- 💬 **AI 智能对话** - 集成阿里云百炼，提供智能问答和会议辅助
- 📝 **会议管理** - 创建、管理备课会议，支持多阶段会议流程
- 📄 **文档管理** - 上传和管理备课资料，支持多种文档格式
- 👥 **教师管理** - 管理参与会议的教师信息
- 📊 **会议总结** - 自动生成会议摘要和要点提取
- 🔐 **用户认证** - JWT 认证，支持用户注册登录

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite + Tailwind CSS
- Socket.IO Client（实时通信）
- Vue Router（路由管理）

### 后端
- Flask + Python 3.13
- Flask-SocketIO（WebSocket 支持）
- SQLAlchemy（ORM）
- MySQL（数据库）
- JWT（身份认证）

### 第三方服务
- 阿里云通义听悟（实时语音转写）
- 阿里云百炼（AI 对话）
- 科大讯飞（ASR、声纹识别）

## 快速开始

### 环境要求

- Docker & Docker Compose
- Node.js 18+（本地开发）
- Python 3.13+（本地开发）

### 配置环境变量

在 `server/.env` 文件中配置以下必需项：

```env
# 阿里云配置（必需）
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
TYTINGWU_APP_KEY=your_tytingwu_app_key

# 阿里云百炼配置（AI 对话功能）
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_APP_ID=your_app_id

# SerpApi 网页搜索（相关资料搜索）https://serpapi.com/search-api
SERPAPI_API_KEY=your_serpapi_api_key

# 应用密钥
SECRET_KEY=your_secret_key

# 数据库配置（可选，有默认值）
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=teacher_preparation
MYSQL_USER=teacher_user
MYSQL_PASSWORD=teacher_password
```

### 使用 Docker Compose 启动

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务启动后：
- 前端：https://localhost:5173
- 后端 API：http://localhost:5001
- phpMyAdmin：http://localhost:8080

### 本地开发

#### 后端开发

```bash
cd server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装阿里云 SDK（需要先下载 whl 文件）
pip install ../nls-1.1.0-py3-none-any.whl

# 启动服务
python app.py
```

#### 前端开发

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器（HTTPS）
pnpm dev
```

## 项目结构

```
teacher-preparation/
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 通用组件
│   │   ├── services/     # API 服务
│   │   └── routes.ts     # 路由配置
│   └── vite.config.js    # Vite 配置（已启用 HTTPS）
│
├── server/                # 后端项目
│   ├── app.py            # Flask 应用入口
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库配置
│   ├── requirements.txt  # Python 依赖
│   ├── docs/             # 文档目录
│   ├── migrations/       # 数据库迁移文件
│   ├── models/           # 数据模型（ORM）
│   ├── routes/           # API 路由（Blueprint）
│   ├── services/         # 业务逻辑服务层
│   ├── utils/            # 工具函数
│   ├── scripts/          # 脚本文件
│   │   └── legacy/       # 旧脚本备份
│   ├── tests/            # 测试文件
│   └── uploads/          # 上传文件存储
│
├── docker-compose.yml    # Docker 编排配置
└── README.md            # 项目说明
```

详细的后端目录结构说明请参考：`server/docs/DIRECTORY_STRUCTURE.md`

## 主要 API 端点

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/meetings` - 获取会议列表
- `POST /api/meetings` - 创建会议
- `GET /api/meetings/:id` - 获取会议详情
- `POST /api/documents` - 上传文档
- `POST /api/ai-chat` - AI 对话
- `GET /api/swagger.json` - API 文档（Swagger）

## 数据库迁移

本项目使用 **Flask-Migrate** 进行数据库迁移管理，替代了之前的手动迁移脚本方式。

### 首次使用

```bash
cd server

# 初始化迁移目录（仅首次需要）
flask db init

# 创建初始迁移（如果数据库已存在表结构）
flask db migrate -m "初始数据库结构"

# 应用迁移（迁移会在应用启动时自动执行）
flask db upgrade
```

### 创建新迁移

当模型发生变化时：

```bash
# 创建迁移文件
flask db migrate -m "迁移描述"

# 应用迁移
flask db upgrade
```

### 迁移管理

- 迁移会在应用启动时**自动执行**
- 所有迁移文件位于 `server/migrations/versions/` 目录
- 迁移按时间顺序执行，确保数据库结构一致性
- 详细文档请参考：`server/migrations/MIGRATION_GUIDE.md`

## 注意事项

1. **HTTPS 配置**：前端开发服务器已配置 HTTPS，首次访问浏览器可能提示证书警告，这是正常的本地开发证书
2. **数据库初始化**：首次启动会自动创建数据库表结构，迁移会在启动时自动执行
3. **阿里云 SDK**：需要手动下载 `nls-1.1.0-py3-none-any.whl` 文件并放在项目根目录
4. **端口冲突**：如果端口被占用，可在 `docker-compose.yml` 中修改端口映射
5. **数据库迁移**：使用 Flask-Migrate 管理数据库变更，不再需要手动执行 `add_*.py` 脚本

## 许可证

[根据项目实际情况填写]

