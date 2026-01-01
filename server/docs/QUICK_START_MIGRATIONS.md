# 数据库迁移快速开始指南

## 前置条件

确保已安装所有依赖：

```bash
cd server
pip install -r requirements.txt
```

## 使用 Flask CLI（推荐）

### 1. 设置环境变量

```bash
# Linux/macOS
export FLASK_APP=app.py

# Windows
set FLASK_APP=app.py
```

或者在项目根目录创建 `.flaskenv` 文件：

```env
FLASK_APP=app.py
FLASK_DEBUG=True
```

### 2. 初始化迁移目录（仅首次需要）

```bash
flask db init
```

这会创建 `migrations/` 目录结构。

### 3. 创建初始迁移

如果数据库已存在表结构：

```bash
flask db migrate -m "初始数据库结构"
```

如果是全新数据库，可以跳过此步骤，直接运行应用（会自动创建表）。

### 4. 应用迁移

迁移会在应用启动时**自动执行**，也可以手动执行：

```bash
flask db upgrade
```

### 5. 创建新迁移

当模型发生变化时：

```bash
flask db migrate -m "添加新字段"
flask db upgrade
```

## 使用 Python 脚本（备选方案）

如果不想使用 Flask CLI，可以使用提供的脚本：

### 初始化迁移目录

```bash
python scripts/init_migrations.py
```

### 创建迁移文件

```bash
python scripts/create_migration.py -m "迁移描述"
```

## 常用命令

```bash
# 查看迁移历史
flask db history

# 查看当前版本
flask db current

# 升级到最新版本
flask db upgrade

# 回滚一个版本
flask db downgrade

# 升级到指定版本
flask db upgrade <revision>

# 回滚到指定版本
flask db downgrade <revision>
```

## 故障排除

### 问题：`flask: command not found`

**解决方案**：确保已安装 Flask，并且虚拟环境已激活。

```bash
pip install Flask Flask-Migrate
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 问题：`No such command 'db'`

**解决方案**：确保已安装 Flask-Migrate。

```bash
pip install Flask-Migrate
```

### 问题：`Could not locate a Flask application`

**解决方案**：设置 `FLASK_APP` 环境变量。

```bash
export FLASK_APP=app.py  # Linux/macOS
set FLASK_APP=app.py  # Windows
```

### 问题：迁移目录不存在

**解决方案**：运行初始化命令。

```bash
flask db init
```

## 注意事项

1. **首次运行**：如果迁移目录不存在，应用会显示警告但不会失败
2. **生产环境**：建议在生产环境手动执行迁移，而不是依赖自动执行
3. **备份数据**：重要数据迁移前请备份数据库
4. **测试迁移**：在测试环境验证迁移后再应用到生产环境

## 更多信息

详细文档请参考：
- `migrations/MIGRATION_GUIDE.md` - 完整迁移指南
- `MIGRATION_SUMMARY.md` - 迁移系统升级总结

