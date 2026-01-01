#!/usr/bin/env python3
"""
数据库迁移脚本：为 meetings 表添加 grade 和 lesson_type 字段
支持 SQLite 和 MySQL
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db

def add_grade_and_lesson_type_columns():
    """为 meetings 表添加 grade 和 lesson_type 字段"""
    with app.app_context():
        try:
            from sqlalchemy import inspect, text
            
            # 获取数据库URL和类型
            db_url = str(db.engine.url)
            print(f"数据库URL: {db_url}")
            
            # 检查字段是否已存在
            grade_exists = False
            lesson_type_exists = False
            try:
                inspector = inspect(db.engine)
                columns = [col['name'] for col in inspector.get_columns('meetings')]
                
                grade_exists = 'grade' in columns
                lesson_type_exists = 'lesson_type' in columns
                
                if grade_exists and lesson_type_exists:
                    print("✅ grade 和 lesson_type 字段已存在，无需添加")
                    return
                
                if grade_exists:
                    print("✅ grade 字段已存在")
                if lesson_type_exists:
                    print("✅ lesson_type 字段已存在")
            except Exception as e:
                print(f"⚠️  检查字段时出错（继续执行）: {str(e)}")
            
            # 检测数据库类型
            is_mysql = 'mysql' in db_url.lower() or 'pymysql' in db_url.lower()
            is_sqlite = 'sqlite' in db_url.lower()
            
            if is_mysql:
                # MySQL 语法
                sql_statements = []
                if not grade_exists:
                    sql_statements.append("ALTER TABLE meetings ADD COLUMN grade VARCHAR(50) NULL")
                if not lesson_type_exists:
                    sql_statements.append("ALTER TABLE meetings ADD COLUMN lesson_type VARCHAR(50) NULL")
                print("检测到 MySQL 数据库，使用 MySQL 语法")
            elif is_sqlite:
                # SQLite 语法
                sql_statements = []
                if not grade_exists:
                    sql_statements.append("ALTER TABLE meetings ADD COLUMN grade VARCHAR(50)")
                if not lesson_type_exists:
                    sql_statements.append("ALTER TABLE meetings ADD COLUMN lesson_type VARCHAR(50)")
                print("检测到 SQLite 数据库，使用 SQLite 语法")
            else:
                # 默认使用 MySQL 语法
                sql_statements = []
                if not grade_exists:
                    sql_statements.append("ALTER TABLE meetings ADD COLUMN grade VARCHAR(50) NULL")
                if not lesson_type_exists:
                    sql_statements.append("ALTER TABLE meetings ADD COLUMN lesson_type VARCHAR(50) NULL")
                print(f"未知数据库类型 ({db_url})，使用 MySQL 语法")
            
            # 执行 SQL
            for sql in sql_statements:
                print(f"执行SQL: {sql}")
                try:
                    db.session.execute(text(sql))
                    db.session.commit()
                    print(f"✅ 成功执行: {sql}")
                except Exception as e:
                    db.session.rollback()
                    error_str = str(e).lower()
                    # 如果是字段已存在的错误，忽略
                    if any(keyword in error_str for keyword in ['duplicate column', 'already exists', 'duplicate', 'column already', '1060']):
                        print(f"✅ 字段已存在（从错误信息判断），跳过: {sql}")
                    else:
                        print(f"❌ 执行失败: {sql}")
                        print(f"错误: {str(e)}")
                        raise
            
            print("✅ 迁移完成！")
            
        except Exception as e:
            print(f"❌ 迁移失败: {str(e)}")
            db.session.rollback()
            print(f"\n详细错误信息:")
            print(f"数据库URL: {db.engine.url}")
            print(f"错误类型: {type(e).__name__}")
            print(f"\n如果字段确实不存在，请手动执行以下SQL:")
            if is_mysql:
                print("  ALTER TABLE meetings ADD COLUMN grade VARCHAR(50) NULL;")
                print("  ALTER TABLE meetings ADD COLUMN lesson_type VARCHAR(50) NULL;")
            else:
                print("  ALTER TABLE meetings ADD COLUMN grade VARCHAR(50);")
                print("  ALTER TABLE meetings ADD COLUMN lesson_type VARCHAR(50);")
            raise

if __name__ == '__main__':
    add_grade_and_lesson_type_columns()

