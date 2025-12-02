"""
数据库配置
"""
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()


def init_db(app):
    """初始化数据库"""
    # 数据库配置
    db_path = os.path.join(os.path.dirname(__file__), 'meetings.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{db_path}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化SQLAlchemy
    db.init_app(app)
    
    # 导入所有模型（确保 SQLAlchemy 知道所有表结构）
    from models import User, Meeting, Transcript, Teacher, Document
    
    # 创建表
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("数据库初始化完成，所有表已创建")
        except Exception as e:
            app.logger.error(f"数据库初始化失败: {str(e)}")
            raise


def get_db():
    """获取数据库实例"""
    return db

