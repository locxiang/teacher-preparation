#!/usr/bin/env python3
"""
数据库初始化脚本
用于手动初始化数据库表结构
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db
from models import User, Meeting, Transcript, Teacher, Document, MeetingTeacher

def init_database():
    """初始化数据库表"""
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功！")
            print("已创建的表:")
            print("  - users")
            print("  - meetings")
            print("  - transcripts")
            print("  - teachers")
            print("  - documents")
            print("  - meeting_teachers")
        except Exception as e:
            print(f"❌ 数据库初始化失败: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    init_database()

