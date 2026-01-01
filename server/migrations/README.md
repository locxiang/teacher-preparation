# 数据库迁移管理

本项目使用 Flask-Migrate 进行数据库迁移管理。

## 初始化（首次使用）

如果是首次使用，需要初始化迁移目录：

```bash
cd server
flask db init
```

## 创建新的迁移

当模型发生变化时，创建新的迁移文件：

```bash
flask db migrate -m "描述信息"
```

例如：
```bash
flask db migrate -m "添加用户头像字段"
```

## 应用迁移

迁移会在应用启动时自动执行。如果需要手动执行：

```bash
flask db upgrade
```

## 回滚迁移

如果需要回滚到上一个版本：

```bash
flask db downgrade
```

回滚到指定版本：

```bash
flask db downgrade <revision>
```

## 查看迁移历史

```bash
flask db history
```

## 查看当前版本

```bash
flask db current
```

## 迁移文件说明

- `versions/` 目录包含所有迁移文件
- 每个迁移文件都有唯一的时间戳和版本号
- 迁移按时间顺序执行，确保数据库结构的一致性

## 注意事项

1. **不要手动修改迁移文件**：除非你非常清楚自己在做什么
2. **测试迁移**：在生产环境应用迁移前，先在测试环境验证
3. **备份数据**：重要数据迁移前请备份数据库
4. **迁移顺序**：迁移文件按时间戳顺序执行，确保依赖关系正确

