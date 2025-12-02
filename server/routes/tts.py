"""
语音合成（TTS）路由
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from services.nls_token_service import NLSTokenService
from config import Config
import logging

logger = logging.getLogger(__name__)

tts_bp = Blueprint('tts', __name__)
token_service = NLSTokenService()


@tts_bp.route('/token', methods=['GET'])
@jwt_required()
def get_tts_token():
    """获取语音合成WebSocket Token"""
    try:
        # 检查配置
        if not Config.ALIBABA_CLOUD_ACCESS_KEY_ID or not Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET:
            return jsonify({
                'success': False,
                'message': '阿里云AccessKey未配置'
            }), 500
        
        if not Config.NLS_APP_KEY:
            return jsonify({
                'success': False,
                'message': 'NLS AppKey未配置，请在环境变量中设置NLS_APP_KEY'
            }), 500
        
        # 生成Token
        token = token_service.generate_token()
        
        return jsonify({
            'success': True,
            'token': token,
            'app_key': Config.NLS_APP_KEY,
            'region': Config.NLS_REGION
        }), 200
        
    except Exception as e:
        logger.error(f"获取TTS Token失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取Token失败: {str(e)}'
        }), 500

