"""
汇总路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

summary_bp = Blueprint('summary', __name__)


@summary_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_summary():
    """生成汇总内容"""
    try:
        user_id = get_jwt_identity()
        
        # 获取上传的文件
        files = request.files.getlist('files')
        
        # 获取聊天记录
        chat_history = request.form.get('chat_history', '')
        
        # 暂时只返回测试内容
        # TODO: 后续实现真正的汇总逻辑
        return jsonify({
            'success': True,
            'summary': '测试的返回内容',
            'message': '汇总生成成功'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成汇总失败: {str(e)}'
        }), 500

