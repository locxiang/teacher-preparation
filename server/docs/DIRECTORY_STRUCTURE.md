# 项目目录结构说明

## 目录组织原则

本项目采用清晰的分层目录结构，便于维护和扩展。

## 目录结构

```
server/
├── app.py                 # Flask 应用主入口文件
├── config.py             # 应用配置管理
├── database.py            # 数据库配置和初始化
├── requirements.txt       # Python 依赖列表
│
├── docs/                  # 文档目录
│   ├── CONFIG_GUIDE.md           # 配置指南
│   ├── MIGRATION_SUMMARY.md     # 迁移系统总结
│   ├── QUICK_START_MIGRATIONS.md # 迁移快速开始
│   ├── README.md                 # 项目说明
│   └── DIRECTORY_STRUCTURE.md    # 本文件
│
├── migrations/            # 数据库迁移文件（Flask-Migrate）
│   ├── versions/          # 迁移版本文件
│   ├── MIGRATION_GUIDE.md # 迁移指南
│   └── README.md          # 迁移说明
│
├── models/                # 数据模型（SQLAlchemy ORM）
│   ├── __init__.py
│   ├── user.py            # 用户模型
│   ├── meeting.py         # 会议模型
│   ├── transcript.py      # 转写记录模型
│   ├── teacher.py         # 教师模型
│   ├── document.py        # 文档模型
│   └── meeting_teacher.py # 会议-教师关联模型
│
├── routes/                # API 路由
│   ├── __init__.py
│   ├── auth.py            # 认证路由
│   ├── meeting.py         # 会议路由
│   ├── document.py        # 文档路由
│   ├── teacher.py         # 教师路由
│   ├── ai_chat.py         # AI 对话路由
│   ├── summary.py         # 摘要路由
│   ├── tts.py             # 语音合成路由
│   ├── tytingwu.py        # 通义听悟路由
│   └── health.py          # 健康检查路由
│
├── services/              # 业务逻辑服务层
│   ├── __init__.py
│   ├── auth_service.py           # 认证服务
│   ├── meeting_service.py         # 会议服务
│   ├── document_service.py       # 文档服务
│   ├── teacher_service.py        # 教师服务
│   ├── websocket_service.py      # WebSocket 服务
│   ├── tytingwu_service.py        # 通义听悟服务
│   ├── tytingwu_websocket.py     # 通义听悟 WebSocket
│   ├── tytingwu_realtime_sdk.py  # 通义听悟实时 SDK
│   ├── nls_token_service.py       # NLS Token 服务
│   └── audio_service.py           # 音频处理服务
│
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── error_handler.py   # 错误处理
│   ├── migration_manager.py # 迁移管理工具
│   └── swagger.py         # Swagger API 文档配置
│
├── scripts/               # 脚本文件
│   ├── init_migrations.py        # 初始化迁移目录
│   ├── create_migration.py       # 创建迁移文件
│   ├── init_db.py                 # 数据库初始化（已废弃，使用迁移系统）
│   ├── run.sh                     # 服务启动脚本
│   └── legacy/                    # 旧脚本备份
│       ├── add_subject_column.py
│       ├── add_grade_and_lesson_type_columns.py
│       ├── add_summary_column.py
│       ├── add_subject_column_mysql.py
│       ├── migrate_add_subject.sql
│       └── check_and_fix_subject_field.sh
│
├── tests/                 # 测试文件
│   ├── __init__.py
│   └── test_api.py        # API 测试
│
├── uploads/               # 上传文件存储目录
│   ├── audio/             # 音频文件
│   └── documents/         # 文档文件
│
└── venv/                  # Python 虚拟环境（不应提交到版本控制）
```

## 目录说明

### 核心文件（根目录）

- `app.py`: Flask 应用主入口，初始化所有组件
- `config.py`: 配置管理，从环境变量读取配置
- `database.py`: 数据库配置和初始化逻辑

### docs/ - 文档目录

存放所有项目文档，包括配置指南、迁移说明等。

### migrations/ - 数据库迁移

使用 Flask-Migrate 管理的数据库迁移文件。所有数据库结构变更都应通过迁移文件进行。

### models/ - 数据模型

SQLAlchemy ORM 模型定义，每个文件对应一个数据库表。

### routes/ - API 路由

Flask 蓝图（Blueprint）定义，每个文件对应一个功能模块的 API 端点。

### services/ - 业务逻辑

业务逻辑实现，与数据库交互、调用第三方服务等。

### utils/ - 工具函数

通用工具函数和辅助模块。

### scripts/ - 脚本文件

各种辅助脚本：
- `init_migrations.py`: 初始化迁移目录
- `create_migration.py`: 创建迁移文件
- `run.sh`: 服务启动脚本
- `legacy/`: 旧脚本备份（已废弃）

### tests/ - 测试文件

单元测试和集成测试。

### uploads/ - 上传文件

用户上传的文件存储目录，不应提交到版本控制。

## 文件命名规范

- Python 文件使用小写字母和下划线：`user_service.py`
- 类名使用大驼峰：`UserService`
- 函数名使用小写字母和下划线：`get_user_by_id`
- 常量使用大写字母和下划线：`MAX_FILE_SIZE`

## 导入路径规范

### 绝对导入（推荐）

```python
from models.user import User
from services.auth_service import AuthService
from utils.error_handler import register_error_handlers
```

### 相对导入（仅在包内使用）

```python
from .user import User  # 在同一包内
from ..services import AuthService  # 从上级包导入
```

## 注意事项

1. **不要修改核心目录结构**：除非有充分的理由
2. **新文件放在合适的目录**：根据文件类型选择正确的目录
3. **保持目录整洁**：定期清理不需要的文件
4. **文档及时更新**：目录结构变化时更新本文档

## 迁移指南

如果需要在不同目录之间移动文件：

1. 移动文件到新位置
2. 更新所有导入路径
3. 运行测试确保功能正常
4. 更新相关文档

