#!/usr/bin/env python3
"""
初始化数据库迁移目录
运行此脚本以初始化 Flask-Migrate 迁移目录结构
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_migrate import init
from app import app

def init_migration_directory():
    """初始化迁移目录"""
    with app.app_context():
        try:
            migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')
            
            # 检查是否已存在
            if os.path.exists(migrations_dir):
                print(f"⚠️  迁移目录已存在: {migrations_dir}")
                print("如果这是首次运行，可以删除该目录后重新运行此脚本")
                return False
            
            # 初始化迁移目录
            init(directory=migrations_dir)
            print(f"✅ 迁移目录初始化成功: {migrations_dir}")
            print("\n下一步:")
            print("1. 创建初始迁移: flask db migrate -m '初始数据库结构'")
            print("2. 应用迁移: flask db upgrade")
            return True
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_migration_directory()
    sys.exit(0 if success else 1)

