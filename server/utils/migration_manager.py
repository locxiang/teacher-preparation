"""
数据库迁移管理工具
在应用启动时自动执行数据库迁移
"""
import os
import logging
from flask_migrate import upgrade

logger = logging.getLogger(__name__)


def run_migrations(app):
    """
    执行数据库迁移
    
    Args:
        app: Flask应用实例
    """
    with app.app_context():
        migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations')
        versions_dir = os.path.join(migrations_dir, 'versions')
        
        # 检查迁移目录是否存在
        if not os.path.exists(migrations_dir):
            logger.warning("迁移目录不存在，跳过自动迁移。请先运行: flask db init")
            return False
        
        # 检查是否有迁移文件
        if os.path.exists(versions_dir):
            version_files = [f for f in os.listdir(versions_dir) if f.endswith('.py')]
            if not version_files:
                logger.info("没有待执行的迁移文件")
                return True
        
        try:
            # 执行迁移
            upgrade()
            logger.info("✓ 数据库迁移执行成功")
            return True
        except Exception as e:
            error_msg = str(e).lower()
            
            # 如果是迁移目录不存在或没有迁移文件，这是正常的
            if 'no such file' in error_msg or 'migrations' in error_msg:
                logger.info("迁移目录未初始化，这是正常的（首次运行或新环境）")
                logger.info("提示: 如需使用迁移功能，请先运行: flask db init")
                return True
            
            # 如果是数据库连接问题
            if 'operationalerror' in error_msg or 'connection' in error_msg:
                logger.error(f"数据库连接失败，无法执行迁移: {str(e)}")
                return False
            
            # 其他错误
            logger.error(f"数据库迁移执行失败: {str(e)}")
            logger.exception("迁移异常详情:")
            return False

