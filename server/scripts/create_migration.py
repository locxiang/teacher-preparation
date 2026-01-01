#!/usr/bin/env python3
"""
创建数据库迁移文件
用法: python scripts/create_migration.py -m "迁移描述"
"""
import sys
import os
import argparse

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_migrate import migrate
from app import app

def create_migration(message):
    """创建迁移文件"""
    with app.app_context():
        try:
            migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')
            
            # 检查迁移目录是否存在
            if not os.path.exists(migrations_dir):
                print("❌ 迁移目录不存在，请先运行: python scripts/init_migrations.py")
                return False
            
            # 创建迁移
            migrate(message=message, directory=migrations_dir)
            print(f"✅ 迁移文件创建成功")
            print(f"   描述: {message}")
            print(f"\n下一步: flask db upgrade")
            return True
        except Exception as e:
            print(f"❌ 创建迁移失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='创建数据库迁移文件')
    parser.add_argument('-m', '--message', required=True, help='迁移描述信息')
    args = parser.parse_args()
    
    success = create_migration(args.message)
    sys.exit(0 if success else 1)

