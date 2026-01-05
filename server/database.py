"""
数据库配置
自动适配数据库结构：启动时自动创建表和字段
"""
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
import logging
from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)

db = SQLAlchemy()


def _get_mysql_column_type(column):
    """
    将 SQLAlchemy 列类型转换为 MySQL 类型字符串
    
    Args:
        column: SQLAlchemy Column 对象
        
    Returns:
        MySQL 类型字符串，如 'VARCHAR(200)', 'INT', 'TEXT', 'DATETIME' 等
    """
    col_type = column.type
    
    # 获取类型名称
    type_name = str(col_type)
    
    # 处理常见类型
    if 'VARCHAR' in type_name or 'String' in type_name:
        length = getattr(col_type, 'length', None)
        if length:
            return f'VARCHAR({length})'
        return 'VARCHAR(255)'
    elif 'TEXT' in type_name:
        # 检查是否是 LONGTEXT（通过 length=None 判断）
        length = getattr(col_type, 'length', None)
        if length is None and 'Text' in type_name:
            return 'LONGTEXT'
        return 'TEXT'
    elif 'INTEGER' in type_name or 'Integer' in type_name:
        return 'INT'
    elif 'BOOLEAN' in type_name or 'Boolean' in type_name:
        return 'BOOLEAN'
    elif 'FLOAT' in type_name or 'Float' in type_name:
        return 'FLOAT'
    elif 'DATETIME' in type_name or 'DateTime' in type_name:
        return 'DATETIME'
    elif 'TIMESTAMP' in type_name:
        return 'TIMESTAMP'
    else:
        # 默认返回原始类型字符串
        return str(col_type)


def _get_mysql_column_definition(column):
    """
    生成 MySQL 列定义字符串
    
    Args:
        column: SQLAlchemy Column 对象
        
    Returns:
        MySQL 列定义字符串，如 'VARCHAR(200) NOT NULL DEFAULT '''
    """
    col_type = _get_mysql_column_type(column)
    
    # 构建列定义
    parts = [col_type]
    
    # NULL/NOT NULL
    if column.nullable:
        parts.append('NULL')
    else:
        parts.append('NOT NULL')
    
    # 默认值处理
    if column.default is not None:
        default = column.default
        
        # 处理可调用的默认值（如 datetime.utcnow）
        if hasattr(default, 'arg'):
            default_value = default.arg
            # 如果是可调用对象（如 datetime.utcnow 或 beijing_now），MySQL 使用 CURRENT_TIMESTAMP
            if callable(default_value):
                if 'datetime' in str(default_value).lower() or 'utcnow' in str(default_value).lower() or 'beijing_now' in str(default_value).lower():
                    parts.append('DEFAULT CURRENT_TIMESTAMP')
                else:
                    # 其他可调用对象，暂时不设置默认值
                    pass
            elif isinstance(default_value, str):
                parts.append(f"DEFAULT '{default_value}'")
            elif default_value is not None:
                parts.append(f'DEFAULT {default_value}')
        else:
            # 直接是值的情况
            if isinstance(default, str):
                parts.append(f"DEFAULT '{default}'")
            elif default is not None:
                parts.append(f'DEFAULT {default}')
    
    # 处理 onupdate（如 updated_at 字段）
    if column.onupdate is not None:
        onupdate = column.onupdate
        if hasattr(onupdate, 'arg') and callable(onupdate.arg):
            if 'datetime' in str(onupdate.arg).lower() or 'utcnow' in str(onupdate.arg).lower() or 'beijing_now' in str(onupdate.arg).lower():
                # MySQL 使用 ON UPDATE CURRENT_TIMESTAMP
                parts.append('ON UPDATE CURRENT_TIMESTAMP')
    
    return ' '.join(parts)


def _check_and_add_columns(app, model_class):
    """
    检查表是否存在所有字段，如果不存在则自动添加
    
    Args:
        app: Flask 应用实例
        model_class: SQLAlchemy 模型类
    """
    table_name = model_class.__tablename__
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # 检查表是否存在
        if not inspector.has_table(table_name):
            logger.info(f"表 {table_name} 不存在，将在创建表时自动创建所有字段")
            return
        
        # 获取现有字段列表
        existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
        
        # 获取模型定义的所有字段
        model_columns = model_class.__table__.columns
        
        # 检查每个字段是否存在
        for column_name, column in model_columns.items():
            if column_name not in existing_columns:
                try:
                    # 生成 ALTER TABLE 语句
                    column_def = _get_mysql_column_definition(column)
                    
                    # 构建 ADD COLUMN 语句
                    alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_def}"
                    
                    # 如果有外键约束，在添加字段后添加外键约束
                    foreign_key = None
                    for fk in model_class.__table__.foreign_keys:
                        if fk.parent.name == column_name:
                            foreign_key = fk
                            break
                    
                    # 执行 SQL
                    with db.engine.connect() as conn:
                        # 添加字段
                        conn.execute(text(alter_sql))
                        
                        # 如果有外键约束，添加外键约束
                        if foreign_key:
                            fk_name = f"fk_{table_name}_{column_name}"
                            fk_sql = (
                                f"ALTER TABLE `{table_name}` "
                                f"ADD CONSTRAINT `{fk_name}` "
                                f"FOREIGN KEY (`{column_name}`) "
                                f"REFERENCES `{foreign_key.column.table.name}` (`{foreign_key.column.name}`)"
                            )
                            try:
                                conn.execute(text(fk_sql))
                                logger.info(f"  └─ 已添加外键约束: {fk_name}")
                            except Exception as fk_e:
                                # 外键约束可能已存在，忽略错误
                                logger.debug(f"  外键约束添加跳过（可能已存在）: {str(fk_e)}")
                        
                        conn.commit()
                    
                    logger.info(f"✓ 已为表 {table_name} 添加字段: {column_name} ({column_def})")
                except Exception as e:
                    logger.error(f"✗ 为表 {table_name} 添加字段 {column_name} 失败: {str(e)}")
                    # 继续处理其他字段，不中断


def _check_and_create_tables(app):
    """
    创建所有表（如果不存在）
    
    Args:
        app: Flask 应用实例
    """
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            logger.info("✓ 数据库表检查完成")
        except Exception as e:
            logger.error(f"✗ 创建数据库表失败: {str(e)}")
            raise


def init_db(app):
    """
    初始化数据库
    自动创建表和字段，让数据库自动适配代码
    """
    # 数据库配置
    database_url = os.getenv(
        'DATABASE_URL',
        app.config.get('SQLALCHEMY_DATABASE_URI', 'mysql://user:password@localhost/dbname')
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化SQLAlchemy
    db.init_app(app)
    
    # 设置数据库连接时区为北京时间（UTC+8）
    # 使用事件监听器，在每次连接建立后自动设置时区
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    
    @event.listens_for(Engine, "connect")
    def set_timezone(dbapi_conn, connection_record):
        """在连接建立后设置时区为北京时间（UTC+8）"""
        cursor = dbapi_conn.cursor()
        cursor.execute("SET time_zone = '+08:00'")
        cursor.close()
    
    # 导入所有模型（确保 SQLAlchemy 知道所有表结构）
    from models import User, Meeting, Transcript, Teacher, Document, MeetingTeacher
    
    # 在应用上下文中执行数据库初始化
    with app.app_context():
        logger.info("开始初始化数据库...")
        
        # 1. 创建所有表（如果不存在）
        _check_and_create_tables(app)
        
        # 2. 检查每个模型的字段，自动添加缺失的字段
        models = [User, Meeting, Transcript, Teacher, Document, MeetingTeacher]
        for model_class in models:
            _check_and_add_columns(app, model_class)
        
        logger.info("✓ 数据库初始化完成，所有表和字段已就绪")


def get_db():
    """获取数据库实例"""
    return db

