"""
用户认证路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from config import Config

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'message': '用户名、邮箱和密码不能为空'
            }), 400
        
        result = auth_service.register(username, email, password)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '注册成功'
        }), 201
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not password:
            return jsonify({
                'success': False,
                'message': '密码不能为空'
            }), 400
        
        result = auth_service.login(username=username, email=email, password=password)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '登录成功'
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    try:
        user_id = get_jwt_identity()
        user = auth_service.get_user(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """获取用户列表"""
    try:
        users = auth_service.list_users()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    """更新用户状态"""
    try:
        data = request.get_json() or {}
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({
                'success': False,
                'message': 'is_active 参数不能为空'
            }), 400
        
        user = auth_service.update_user_status(user_id, is_active)
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': '用户状态更新成功'
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    try:
        auth_service.delete_user(user_id)
        return jsonify({
            'success': True,
            'message': '用户删除成功'
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def mask_secret(secret: str, show_chars: int = 4) -> str:
    """掩码显示密钥，只显示前后几个字符"""
    if not secret:
        return '未设置'
    if len(secret) <= show_chars * 2:
        return '*' * len(secret)
    return f"{secret[:show_chars]}...{secret[-show_chars:]}"


@auth_bp.route('/api-keys', methods=['GET'])
@jwt_required()
def get_api_keys():
    """获取API密钥信息（掩码显示）"""
    try:
        api_keys = {
            'backend': {
                'alibaba_cloud': {
                    'access_key_id': {
                        'name': '阿里云 AccessKey ID',
                        'value': mask_secret(Config.ALIBABA_CLOUD_ACCESS_KEY_ID or ''),
                        'is_set': bool(Config.ALIBABA_CLOUD_ACCESS_KEY_ID),
                        'full_value': Config.ALIBABA_CLOUD_ACCESS_KEY_ID or None,
                    },
                    'access_key_secret': {
                        'name': '阿里云 AccessKey Secret',
                        'value': mask_secret(Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET or ''),
                        'is_set': bool(Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET),
                        'full_value': Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET or None,
                    },
                },
                'tytingwu': {
                    'app_key': {
                        'name': '通义听悟 AppKey',
                        'value': mask_secret(Config.TYTINGWU_APP_KEY or ''),
                        'is_set': bool(Config.TYTINGWU_APP_KEY),
                        'full_value': Config.TYTINGWU_APP_KEY or None,
                    },
                },
                'nls': {
                    'app_key': {
                        'name': '智能语音交互 AppKey',
                        'value': mask_secret(Config.NLS_APP_KEY or ''),
                        'is_set': bool(Config.NLS_APP_KEY),
                        'full_value': Config.NLS_APP_KEY or None,
                    },
                },
                'dashscope': {
                    'api_key': {
                        'name': 'DashScope API Key',
                        'value': mask_secret(Config.DASHSCOPE_API_KEY or ''),
                        'is_set': bool(Config.DASHSCOPE_API_KEY),
                        'full_value': Config.DASHSCOPE_API_KEY or None,
                    },
                    'app_id': {
                        'name': 'DashScope App ID',
                        'value': mask_secret(Config.DASHSCOPE_APP_ID or ''),
                        'is_set': bool(Config.DASHSCOPE_APP_ID),
                        'full_value': Config.DASHSCOPE_APP_ID or None,
                    },
                },
                'flask': {
                    'secret_key': {
                        'name': 'Flask Secret Key',
                        'value': mask_secret(Config.SECRET_KEY or ''),
                        'is_set': bool(Config.SECRET_KEY and Config.SECRET_KEY != 'dev-secret-key-change-in-production'),
                        'full_value': Config.SECRET_KEY or None,
                    },
                },
            },
            'frontend': {
                'xunfei': {
                    'app_id': {
                        'name': '科大讯飞 App ID',
                        'value': '前端环境变量',
                        'is_set': None,  # 前端配置，后端无法获取
                        'full_value': None,
                    },
                    'access_key_id': {
                        'name': '科大讯飞 AccessKey ID',
                        'value': '前端环境变量',
                        'is_set': None,
                        'full_value': None,
                    },
                    'access_key_secret': {
                        'name': '科大讯飞 AccessKey Secret',
                        'value': '前端环境变量',
                        'is_set': None,
                        'full_value': None,
                    },
                },
            },
        }
        
        return jsonify({
            'success': True,
            'data': api_keys
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

