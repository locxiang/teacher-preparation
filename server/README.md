# 后端服务

Flask 后端服务，提供 RESTful API 和 WebSocket 支持。

## 快速开始

### 环境要求

- Python 3.13+
- MySQL 或 SQLite

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件或设置环境变量（参考 `docs/CONFIG_GUIDE.md`）。

### 启动服务

```bash
# 方式1: 直接运行
python app.py

# 方式2: 使用启动脚本
bash scripts/run.sh

# 方式3: 使用 Flask CLI
export FLASK_APP=app.py
flask run
```

## 目录结构

详细目录结构说明请参考：`docs/DIRECTORY_STRUCTURE.md`

```
server/
├── app.py              # 应用入口
├── config.py           # 配置管理
├── database.py         # 数据库配置
├── docs/               # 文档
├── migrations/         # 数据库迁移
├── models/             # 数据模型
├── routes/             # API 路由
├── services/           # 业务逻辑
├── utils/              # 工具函数
├── scripts/            # 脚本文件
└── tests/              # 测试文件
```

## 数据库迁移

使用 Flask-Migrate 管理数据库迁移：

```bash
# 初始化（首次使用）
flask db init

# 创建迁移
flask db migrate -m "描述"

# 应用迁移
flask db upgrade
```

详细说明请参考：`docs/QUICK_START_MIGRATIONS.md`

## API 文档

启动服务后访问：http://localhost:5001/api/docs

## 开发指南

### 添加新功能

1. 在 `models/` 中定义数据模型（如需要）
2. 在 `services/` 中实现业务逻辑
3. 在 `routes/` 中定义 API 端点
4. 在 `tests/` 中添加测试

### 代码规范

- 使用类型提示
- 遵循 PEP 8 代码风格
- 添加文档字符串
- 编写单元测试

## 相关文档

- `docs/CONFIG_GUIDE.md` - 配置指南
- `docs/MIGRATION_SUMMARY.md` - 迁移系统说明
- `docs/DIRECTORY_STRUCTURE.md` - 目录结构说明
- `migrations/MIGRATION_GUIDE.md` - 数据库迁移指南

