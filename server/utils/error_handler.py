"""
错误处理工具
"""
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': '请求参数错误',
            'error': str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': '资源不存在',
            'error': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'服务器内部错误: {str(error)}')
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error': str(error) if app.config.get('DEBUG') else 'Internal Server Error'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f'未处理的异常: {str(error)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': '服务器错误',
            'error': str(error) if app.config.get('DEBUG') else 'Server Error'
        }), 500

