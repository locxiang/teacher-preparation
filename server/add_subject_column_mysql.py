#!/usr/bin/env python3
"""
数据库迁移脚本：为 meetings 表添加 subject 字段（MySQL版本）
直接连接到 MySQL 数据库执行迁移
"""
import sys
import os
import pymysql

# 从环境变量或配置中获取 MySQL 连接信息
def get_mysql_config():
    """获取 MySQL 配置"""
    database_url = os.getenv('DATABASE_URL', '')
    
    if not database_url:
        print("❌ 未找到 DATABASE_URL 环境变量")
        print("请设置 DATABASE_URL 环境变量，格式: mysql+pymysql://user:password@host:port/database")
        sys.exit(1)
    
    # 解析 MySQL URL
    # 格式: mysql+pymysql://user:password@host:port/database
    if 'mysql' not in database_url.lower():
        print(f"❌ DATABASE_URL 不是 MySQL 连接: {database_url}")
        sys.exit(1)
    
    # 移除 mysql+pymysql:// 前缀
    url = database_url.replace('mysql+pymysql://', '').replace('mysql://', '')
    
    # 解析
    if '@' in url:
        auth_part, host_part = url.split('@', 1)
        if ':' in auth_part:
            user, password = auth_part.split(':', 1)
        else:
            user = auth_part
            password = ''
        
        if '/' in host_part:
            host_port, database = host_part.split('/', 1)
            if ':' in host_port:
                host, port = host_port.split(':')
                port = int(port)
            else:
                host = host_port
                port = 3306
        else:
            host = host_part
            port = 3306
            database = ''
    else:
        print(f"❌ 无法解析 DATABASE_URL: {database_url}")
        sys.exit(1)
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }

def add_subject_column_mysql():
    """为 MySQL 数据库的 meetings 表添加 subject 字段"""
    try:
        config = get_mysql_config()
        
        print(f"正在连接到 MySQL 数据库: {config['host']}:{config['port']}/{config['database']}")
        
        # 连接到 MySQL
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )
        
        try:
            with connection.cursor() as cursor:
                # 检查字段是否已存在
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'meetings' 
                    AND COLUMN_NAME = 'subject'
                """, (config['database'],))
                
                if cursor.fetchone():
                    print("✅ subject 字段已存在，无需添加")
                    return
                
                # 添加 subject 字段
                cursor.execute("ALTER TABLE meetings ADD COLUMN subject VARCHAR(50) NULL")
                connection.commit()
                print("✅ 成功添加 subject 字段到 meetings 表")
                
        finally:
            connection.close()
            
    except Exception as e:
        print(f"❌ 添加字段失败: {str(e)}")
        print(f"\n详细错误信息:")
        print(f"错误类型: {type(e).__name__}")
        raise

if __name__ == '__main__':
    add_subject_column_mysql()

