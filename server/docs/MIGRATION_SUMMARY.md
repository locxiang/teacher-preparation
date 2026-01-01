# 数据库迁移系统升级总结

## 变更概述

已将数据库迁移管理从手动脚本方式升级为使用 **Flask-Migrate** 的标准化迁移系统。

## 主要改进

### ✅ 之前的方式（已废弃）

- 多个独立的 `add_*.py` 脚本文件
- 需要手动按顺序执行
- 难以追踪迁移历史
- 无法回滚
- 团队协作困难

### ✅ 新的方式（当前）

- 统一的迁移文件管理（`migrations/versions/`）
- 自动按顺序执行
- 完整的迁移历史追踪
- 支持回滚操作
- 版本控制友好

## 文件变更

### 新增文件

1. **`server/utils/migration_manager.py`**
   - 迁移管理工具模块
   - 在应用启动时自动执行迁移

2. **`server/migrations/README.md`**
   - 迁移系统使用说明

3. **`server/migrations/MIGRATION_GUIDE.md`**
   - 详细的迁移指南和最佳实践

4. **`server/migrations/versions/example_migration.py.example`**
   - 迁移文件示例模板

5. **`server/scripts/init_migrations.py`**
   - 初始化迁移目录的脚本

6. **`server/scripts/create_migration.py`**
   - 创建新迁移文件的脚本

### 修改文件

1. **`server/database.py`**
   - 添加 Flask-Migrate 初始化
   - 移除 `db.create_all()`（改用迁移系统）

2. **`server/app.py`**
   - 添加自动迁移执行逻辑

3. **`README.md`**
   - 添加数据库迁移章节

### 保留文件（作为参考）

以下文件可以保留作为参考，但不再需要手动执行：

- `server/add_subject_column.py`
- `server/add_grade_and_lesson_type_columns.py`
- `server/add_summary_column.py`
- `server/add_subject_column_mysql.py`

建议将这些文件移动到 `server/scripts/legacy/` 目录作为备份。

## 使用步骤

### 1. 初始化迁移系统（首次使用）

```bash
cd server
flask db init
```

### 2. 创建初始迁移

如果数据库已存在表结构：

```bash
flask db migrate -m "初始数据库结构"
```

这会扫描所有模型并生成迁移文件。

### 3. 应用迁移

迁移会在应用启动时**自动执行**，也可以手动执行：

```bash
flask db upgrade
```

### 4. 创建新迁移

当模型发生变化时：

```bash
flask db migrate -m "迁移描述"
flask db upgrade
```

## 迁移执行顺序

Flask-Migrate 通过以下机制确保迁移按正确顺序执行：

1. **版本链**：每个迁移文件都有 `revision` 和 `down_revision` 字段
2. **时间戳**：文件名包含时间戳，确保时间顺序
3. **版本表**：数据库中的 `alembic_version` 表记录当前版本
4. **自动检测**：系统自动检测未应用的迁移并执行

## 兼容性说明

### 现有数据库

如果数据库已经存在并且已经执行过旧的迁移脚本：

1. Flask-Migrate 会自动检测现有表结构
2. 创建初始迁移时，只会包含当前模型定义
3. 已存在的字段不会被重复添加（SQLAlchemy 会检测）

### 新数据库

如果是全新的数据库：

1. 初始化迁移目录
2. 创建初始迁移
3. 应用迁移，创建所有表结构

## 优势总结

1. ✅ **统一管理**：所有迁移文件集中管理
2. ✅ **自动执行**：启动时自动应用迁移
3. ✅ **版本控制**：完整的迁移历史
4. ✅ **回滚支持**：可以回滚到任意版本
5. ✅ **团队协作**：迁移文件可提交到 Git
6. ✅ **错误处理**：更好的错误处理和日志记录
7. ✅ **标准化**：使用行业标准的 Alembic 引擎

## 注意事项

1. **首次运行**：如果迁移目录不存在，应用会显示警告但不会失败
2. **生产环境**：建议在生产环境手动执行迁移，而不是依赖自动执行
3. **备份数据**：重要数据迁移前请备份数据库
4. **测试迁移**：在测试环境验证迁移后再应用到生产环境

## 后续工作

1. ✅ 初始化迁移系统
2. ✅ 创建初始迁移文件
3. ⚠️ 将旧的 `add_*.py` 文件移动到 `scripts/legacy/` 目录（可选）
4. ⚠️ 在生产环境测试迁移系统

## 参考文档

- Flask-Migrate 官方文档：https://flask-migrate.readthedocs.io/
- Alembic 文档：https://alembic.sqlalchemy.org/

