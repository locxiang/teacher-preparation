-- 数据库迁移脚本：为 meetings 表添加 subject 字段
-- 适用于 MySQL 数据库

-- 检查字段是否存在，如果不存在则添加
-- 注意：MySQL 不支持 IF NOT EXISTS，所以如果字段已存在会报错，可以忽略

ALTER TABLE meetings ADD COLUMN subject VARCHAR(50) NULL;

-- 如果需要设置默认值，可以使用：
-- ALTER TABLE meetings ADD COLUMN subject VARCHAR(50) NULL DEFAULT NULL;

