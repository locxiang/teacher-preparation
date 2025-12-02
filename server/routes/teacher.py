"""
教师管理路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.teacher_service import TeacherService

teacher_bp = Blueprint('teacher', __name__)
teacher_service = TeacherService()


@teacher_bp.route('', methods=['GET'])
@jwt_required()
def list_teachers():
    """获取教师列表"""
    try:
        user_id = get_jwt_identity()
        teachers = teacher_service.list_teachers(user_id=user_id)
        
        return jsonify({
            'success': True,
            'data': teachers,
            'total': len(teachers)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@teacher_bp.route('', methods=['POST'])
@jwt_required()
def create_teacher():
    """创建教师"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        name = data.get('name')
        subject = data.get('subject')
        
        if not name or not subject:
            return jsonify({
                'success': False,
                'message': '教师姓名和学科不能为空'
            }), 400
        
        teacher = teacher_service.create_teacher(
            name=name,
            subject=subject,
            user_id=user_id,
            feature_id=data.get('feature_id')
        )
        
        return jsonify({
            'success': True,
            'data': teacher
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


@teacher_bp.route('/<int:teacher_id>', methods=['PUT'])
@jwt_required()
def update_teacher(teacher_id):
    """更新教师信息"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        teacher = teacher_service.update_teacher(
            teacher_id=teacher_id,
            user_id=user_id,
            name=data.get('name'),
            subject=data.get('subject'),
            feature_id=data.get('feature_id')
        )
        
        return jsonify({
            'success': True,
            'data': teacher
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@teacher_bp.route('/<int:teacher_id>', methods=['DELETE'])
@jwt_required()
def delete_teacher(teacher_id):
    """删除教师"""
    try:
        user_id = get_jwt_identity()
        teacher_service.delete_teacher(teacher_id=teacher_id, user_id=user_id)
        
        return jsonify({
            'success': True,
            'message': '教师已删除'
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

