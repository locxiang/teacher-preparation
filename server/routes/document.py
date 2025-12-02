"""
文档上传路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import RequestEntityTooLarge
from services.document_service import DocumentService
from services.meeting_service import MeetingService
import os

document_bp = Blueprint('document', __name__)
document_service = DocumentService()
meeting_service = MeetingService()


@document_bp.route('/upload/<meeting_id>', methods=['POST'])
@jwt_required()
def upload_document(meeting_id):
    """上传文档文件"""
    try:
        user_id = get_jwt_identity()
        
        # 检查会议是否存在且属于当前用户
        meeting = meeting_service.get_meeting(meeting_id, user_id=user_id)
        if not meeting:
            return jsonify({
                'success': False,
                'message': '会议不存在或无权限'
            }), 404
        
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '文件名为空'
            }), 400
        
        # 保存文件
        file_path, filename = document_service.save_document_file(file, meeting_id)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 创建文档记录
        document = document_service.create_document_record(
            meeting_id=meeting_id,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': document.to_dict(),
            'message': '文档上传成功'
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'message': '文件大小超过限制（最大20MB）'
        }), 413
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@document_bp.route('/list/<meeting_id>', methods=['GET'])
@jwt_required()
def list_documents(meeting_id):
    """列出会议的所有文档"""
    try:
        user_id = get_jwt_identity()
        
        # 检查会议是否存在且属于当前用户
        meeting = meeting_service.get_meeting(meeting_id, user_id=user_id)
        if not meeting:
            return jsonify({
                'success': False,
                'message': '会议不存在或无权限'
            }), 404
        
        # 获取文档列表
        documents = document_service.get_documents_by_meeting(meeting_id, user_id=user_id)
        
        return jsonify({
            'success': True,
            'data': documents,
            'total': len(documents)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@document_bp.route('/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """删除文档"""
    try:
        user_id = get_jwt_identity()
        
        success = document_service.delete_document(document_id, user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '文档不存在或无权限'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '文档已删除'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

