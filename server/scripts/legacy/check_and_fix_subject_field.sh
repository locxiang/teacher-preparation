#!/bin/bash
# 检查并修复 MySQL 数据库中的 subject 字段

echo "=========================================="
echo "检查并修复 MySQL meetings 表的 subject 字段"
echo "=========================================="
echo ""

# 从 docker-compose.yml 或环境变量获取 MySQL 配置
MYSQL_USER=${MYSQL_USER:-teacher_user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-teacher_password}
MYSQL_DATABASE=${MYSQL_DATABASE:-teacher_preparation}
MYSQL_CONTAINER=${MYSQL_CONTAINER:-teacher_prep_mysql}

echo "MySQL 配置:"
echo "  容器名: $MYSQL_CONTAINER"
echo "  数据库: $MYSQL_DATABASE"
echo "  用户: $MYSQL_USER"
echo ""

# 检查容器是否存在
if ! docker ps -a --format '{{.Names}}' | grep -q "^${MYSQL_CONTAINER}$"; then
    echo "❌ MySQL 容器 '$MYSQL_CONTAINER' 不存在"
    echo "请检查容器名称是否正确，或使用以下命令查看所有容器："
    echo "  docker ps -a"
    exit 1
fi

# 检查容器是否运行
if ! docker ps --format '{{.Names}}' | grep -q "^${MYSQL_CONTAINER}$"; then
    echo "⚠️  MySQL 容器 '$MYSQL_CONTAINER' 未运行，尝试启动..."
    docker start $MYSQL_CONTAINER
    sleep 3
fi

echo "1. 检查 meetings 表结构..."
docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "DESCRIBE meetings;" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ 无法连接到 MySQL 数据库"
    echo "请检查："
    echo "  1. MySQL 容器是否正常运行"
    echo "  2. 数据库用户名和密码是否正确"
    echo "  3. 数据库名称是否正确"
    exit 1
fi

echo ""
echo "2. 检查 subject 字段是否存在..."
SUBJECT_EXISTS=$(docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -N -e "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '$MYSQL_DATABASE' AND TABLE_NAME = 'meetings' AND COLUMN_NAME = 'subject';" 2>/dev/null)

if [ "$SUBJECT_EXISTS" = "1" ]; then
    echo "✅ subject 字段已存在"
    echo ""
    echo "3. 检查字段详细信息..."
    docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "SHOW COLUMNS FROM meetings LIKE 'subject';" 2>/dev/null
else
    echo "⚠️  subject 字段不存在，正在添加..."
    docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "ALTER TABLE meetings ADD COLUMN subject VARCHAR(50) NULL;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ subject 字段添加成功"
        echo ""
        echo "验证字段..."
        docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "SHOW COLUMNS FROM meetings LIKE 'subject';" 2>/dev/null
    else
        echo "❌ subject 字段添加失败"
        echo ""
        echo "请手动执行以下 SQL："
        echo "  ALTER TABLE meetings ADD COLUMN subject VARCHAR(50) NULL;"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="

