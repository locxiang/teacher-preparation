"""
数据库配置
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()


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
    
    # 初始化Flask-Migrate
    migrate.init_app(app, db, directory='migrations')
    
    # 导入所有模型（确保 SQLAlchemy 知道所有表结构）
    from models import User, Meeting, Transcript, Teacher, Document, MeetingTeacher
    
    # 注意：不再使用 db.create_all()，而是使用 Flask-Migrate 进行迁移管理
    # 迁移会在应用启动时自动执行（见 app.py）


def get_db():
    """获取数据库实例"""
    return db

