# 目录结构重构总结

## 重构目标

将 server 目录下混乱的文件组织成清晰、合理的目录结构，提高代码可维护性。

## 重构内容

### 1. 创建新目录

- `docs/` - 统一存放所有文档文件
- `scripts/legacy/` - 存放已废弃的旧脚本

### 2. 文件移动

#### 文档文件 → `docs/`
- `MIGRATION_SUMMARY.md` → `docs/MIGRATION_SUMMARY.md`
- `QUICK_START_MIGRATIONS.md` → `docs/QUICK_START_MIGRATIONS.md`
- `CONFIG_GUIDE.md` → `docs/CONFIG_GUIDE.md`
- `README.md` → `docs/README.md`（保留 server 根目录的 README.md）

#### 旧迁移脚本 → `scripts/legacy/`
- `add_subject_column.py` → `scripts/legacy/add_subject_column.py`
- `add_subject_column_mysql.py` → `scripts/legacy/add_subject_column_mysql.py`
- `add_grade_and_lesson_type_columns.py` → `scripts/legacy/add_grade_and_lesson_type_columns.py`
- `add_summary_column.py` → `scripts/legacy/add_summary_column.py`
- `migrate_add_subject.sql` → `scripts/legacy/migrate_add_subject.sql`
- `check_and_fix_subject_field.sh` → `scripts/legacy/check_and_fix_subject_field.sh`

#### 脚本文件 → `scripts/`
- `run.sh` → `scripts/run.sh`
- `init_db.py` → `scripts/init_db.py`

#### 工具文件 → `utils/`
- `swagger.py` → `utils/swagger.py`

### 3. 代码更新

#### 更新导入路径
- `app.py`: `from swagger import ...` → `from utils.swagger import ...`

#### 修复脚本路径
- `scripts/init_db.py`: 修复路径引用，指向正确的项目根目录
- `scripts/run.sh`: 添加目录切换逻辑，确保在正确目录执行

### 4. 新增文档

- `docs/DIRECTORY_STRUCTURE.md` - 详细的目录结构说明
- `server/README.md` - server 目录的快速开始指南

## 重构后的目录结构

```
server/
├── app.py              # Flask 应用入口（核心文件）
├── config.py           # 配置管理（核心文件）
├── database.py         # 数据库配置（核心文件）
├── requirements.txt    # Python 依赖
├── README.md           # 快速开始指南
│
├── docs/               # 📚 文档目录
│   ├── CONFIG_GUIDE.md
│   ├── DIRECTORY_STRUCTURE.md
│   ├── MIGRATION_SUMMARY.md
│   ├── QUICK_START_MIGRATIONS.md
│   └── README.md
│
├── migrations/          # 🗄️ 数据库迁移
│   ├── versions/
│   ├── MIGRATION_GUIDE.md
│   └── README.md
│
├── models/             # 📊 数据模型
├── routes/             # 🛣️ API 路由
├── services/           # 🔧 业务逻辑
├── utils/              # 🛠️ 工具函数
│   └── swagger.py      # Swagger 配置
│
├── scripts/            # 📜 脚本文件
│   ├── create_migration.py
│   ├── init_db.py
│   ├── init_migrations.py
│   ├── run.sh
│   └── legacy/         # 旧脚本备份
│
├── tests/              # 🧪 测试文件
└── uploads/            # 📁 上传文件存储
```

## 优势

### ✅ 清晰的目录结构
- 核心文件保留在根目录
- 相关文件按类型组织到对应目录
- 易于查找和维护

### ✅ 更好的可维护性
- 文档集中管理
- 脚本统一管理
- 旧代码归档到 legacy 目录

### ✅ 符合最佳实践
- 遵循 Flask 项目标准结构
- 分离关注点（模型、路由、服务）
- 便于团队协作

## 注意事项

1. **导入路径已更新**：所有导入路径已更新，代码应该可以正常运行
2. **旧脚本保留**：旧迁移脚本已移动到 `scripts/legacy/`，作为参考保留
3. **文档位置**：所有文档现在在 `docs/` 目录，便于查找
4. **脚本路径**：`scripts/run.sh` 会自动切换到项目根目录执行

## 验证

重构后已验证：
- ✅ 所有导入路径正确
- ✅ 脚本路径修复完成
- ✅ 目录结构清晰合理
- ✅ 文档完整

## 后续建议

1. **清理旧文件**：如果确认不再需要，可以删除 `scripts/legacy/` 中的文件
2. **添加 .gitignore**：确保 `uploads/` 和 `venv/` 不被提交
3. **持续维护**：保持目录结构整洁，新文件放在合适的位置

