#!/usr/bin/env python3
"""
数据库迁移脚本：为 meetings 表添加 subject 字段
支持 SQLite 和 MySQL
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db

def add_subject_column():
    """为 meetings 表添加 subject 字段"""
    with app.app_context():
        try:
            from sqlalchemy import inspect, text
            
            # 获取数据库URL和类型
            db_url = str(db.engine.url)
            print(f"数据库URL: {db_url}")
            
            # 检查字段是否已存在
            try:
                inspector = inspect(db.engine)
                columns = [col['name'] for col in inspector.get_columns('meetings')]
                
                if 'subject' in columns:
                    print("✅ subject 字段已存在，无需添加")
                    return
            except Exception as e:
                print(f"⚠️  检查字段时出错（继续执行）: {str(e)}")
            
            # 检测数据库类型
            is_mysql = 'mysql' in db_url.lower() or 'pymysql' in db_url.lower()
            is_sqlite = 'sqlite' in db_url.lower()
            
            if is_mysql:
                # MySQL 语法 - 使用 MODIFY 方式更安全
                # 先尝试添加，如果失败说明已存在
                sql = "ALTER TABLE meetings ADD COLUMN subject VARCHAR(50) NULL"
                print("检测到 MySQL 数据库，使用 MySQL 语法")
            elif is_sqlite:
                # SQLite 语法
                sql = "ALTER TABLE meetings ADD COLUMN subject VARCHAR(50)"
                print("检测到 SQLite 数据库，使用 SQLite 语法")
            else:
                # 默认使用 MySQL 语法（因为错误信息显示是 MySQL）
                sql = "ALTER TABLE meetings ADD COLUMN subject VARCHAR(50) NULL"
                print(f"未知数据库类型 ({db_url})，使用 MySQL 语法")
            
            # 执行 SQL
            print(f"执行SQL: {sql}")
            db.session.execute(text(sql))
            db.session.commit()
            print("✅ 成功添加 subject 字段到 meetings 表")
            
        except Exception as e:
            print(f"❌ 添加字段失败: {str(e)}")
            db.session.rollback()
            # 如果是字段已存在的错误，忽略
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['duplicate column', 'already exists', 'duplicate', 'column already', '1060']):
                print("✅ subject 字段已存在（从错误信息判断）")
            else:
                print(f"\n详细错误信息:")
                print(f"数据库URL: {db.engine.url}")
                print(f"错误类型: {type(e).__name__}")
                print(f"\n如果字段确实不存在，请手动执行以下SQL:")
                if is_mysql:
                    print("  ALTER TABLE meetings ADD COLUMN subject VARCHAR(50) NULL;")
                else:
                    print("  ALTER TABLE meetings ADD COLUMN subject VARCHAR(50);")
                raise

if __name__ == '__main__':
    add_subject_column()

