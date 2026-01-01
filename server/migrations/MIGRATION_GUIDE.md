# 数据库迁移指南

## 概述

本项目使用 Flask-Migrate 进行数据库迁移管理，替代了之前的手动 `add_*.py` 脚本方式。

## 优势

1. **统一管理**：所有迁移文件集中在 `migrations/versions/` 目录
2. **版本控制**：每个迁移都有唯一版本号，按时间顺序执行
3. **自动执行**：应用启动时自动执行未应用的迁移
4. **回滚支持**：可以轻松回滚到之前的版本
5. **团队协作**：迁移文件可以提交到版本控制系统

## 快速开始

### 1. 初始化迁移目录（首次使用）

```bash
cd server
python scripts/init_migrations.py
```

或者使用 Flask CLI：

```bash
cd server
flask db init
```

### 2. 创建初始迁移（如果数据库已存在）

如果数据库已经存在表结构，需要创建初始迁移：

```bash
flask db migrate -m "初始数据库结构"
```

这会扫描所有模型并生成迁移文件。

### 3. 应用迁移

迁移会在应用启动时自动执行。也可以手动执行：

```bash
flask db upgrade
```

## 创建新迁移

当模型发生变化时（添加字段、修改字段类型等），创建新迁移：

```bash
# 方法1: 使用 Flask CLI
flask db migrate -m "添加用户头像字段"

# 方法2: 使用脚本
python scripts/create_migration.py -m "添加用户头像字段"
```

## 迁移文件示例

迁移文件位于 `migrations/versions/` 目录，文件名格式为：
`<时间戳>_<描述>.py`

示例：

```python
"""添加 subject 字段到 meetings 表

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    # 添加字段
    op.add_column('meetings', sa.Column('subject', sa.String(length=50), nullable=True))

def downgrade():
    # 删除字段
    op.drop_column('meetings', 'subject')
```

## 将旧迁移转换为新格式

### 已完成的迁移

以下迁移已经完成，不需要再次执行：

1. ✅ `add_subject_column.py` - 添加 `subject` 字段到 `meetings` 表
2. ✅ `add_grade_and_lesson_type_columns.py` - 添加 `grade` 和 `lesson_type` 字段到 `meetings` 表
3. ✅ `add_summary_column.py` - 添加 `summary` 字段到 `documents` 表

这些迁移已经应用到现有数据库中，在创建初始迁移时，Flask-Migrate 会自动检测到这些字段已存在。

### 如果需要在迁移文件中包含这些变更

如果数据库是全新的，可以在初始迁移中包含所有字段。如果数据库已经存在，Flask-Migrate 会自动检测差异。

## 常用命令

```bash
# 查看迁移历史
flask db history

# 查看当前版本
flask db current

# 升级到最新版本
flask db upgrade

# 升级到指定版本
flask db upgrade <revision>

# 回滚一个版本
flask db downgrade

# 回滚到指定版本
flask db downgrade <revision>

# 显示迁移SQL（不实际执行）
flask db upgrade --sql

# 显示回滚SQL（不实际执行）
flask db downgrade --sql
```

## 注意事项

1. **不要手动修改迁移文件**：除非你非常清楚自己在做什么
2. **测试迁移**：在生产环境应用迁移前，先在测试环境验证
3. **备份数据**：重要数据迁移前请备份数据库
4. **迁移顺序**：迁移文件按时间戳顺序执行，确保依赖关系正确
5. **团队协作**：迁移文件应该提交到版本控制系统，团队成员需要同步执行

## 故障排除

### 迁移目录不存在

如果看到 "迁移目录不存在" 的警告，运行：

```bash
python scripts/init_migrations.py
```

### 迁移冲突

如果多个开发者同时创建迁移，可能出现冲突。解决方式：

1. 拉取最新的迁移文件
2. 如果有冲突，手动合并迁移文件
3. 确保迁移顺序正确

### 迁移失败

如果迁移失败：

1. 检查错误信息
2. 如果是字段已存在，可以手动编辑迁移文件，添加检查逻辑
3. 或者回滚迁移，修复问题后重新创建

## 旧迁移脚本处理

旧的 `add_*.py` 脚本可以保留作为参考，但不再需要手动执行。新的迁移系统会自动处理所有数据库变更。

如果需要，可以将这些脚本移动到 `scripts/legacy/` 目录作为备份。

