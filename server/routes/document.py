"""
文档上传路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import RequestEntityTooLarge
from services.document_service import DocumentService
from services.meeting_service import MeetingService
import os
import threading
import logging

logger = logging.getLogger(__name__)

document_bp = Blueprint('document', __name__)
document_service = DocumentService()
meeting_service = MeetingService()


@document_bp.route('/upload/<meeting_id>', methods=['POST'])
@jwt_required()
def upload_document(meeting_id):
    """上传文档文件"""
    try:
        user_id = get_jwt_identity()
        logger.info(f"[文档上传] 开始处理上传请求 - meeting_id: {meeting_id}, user_id: {user_id}")
        
        # 检查会议是否存在且属于当前用户
        logger.debug(f"[文档上传] 检查会议是否存在 - meeting_id: {meeting_id}")
        meeting = meeting_service.get_meeting(meeting_id, user_id=user_id)
        if not meeting:
            logger.warning(f"[文档上传] 会议不存在或无权限 - meeting_id: {meeting_id}, user_id: {user_id}")
            return jsonify({
                'success': False,
                'message': '会议不存在或无权限'
            }), 404
        
        logger.debug(f"[文档上传] 会议验证通过 - meeting_id: {meeting_id}")
        
        # 检查文件是否存在
        if 'file' not in request.files:
            logger.warning(f"[文档上传] 请求中没有文件 - meeting_id: {meeting_id}")
            return jsonify({
                'success': False,
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        logger.info(f"[文档上传] 收到文件 - filename: {file.filename}, content_type: {file.content_type}")
        
        if file.filename == '':
            logger.warning(f"[文档上传] 文件名为空 - meeting_id: {meeting_id}")
            return jsonify({
                'success': False,
                'message': '文件名为空'
            }), 400
        
        # 保存文件
        logger.debug(f"[文档上传] 开始保存文件 - filename: {file.filename}")
        file_path, filename = document_service.save_document_file(file, meeting_id)
        logger.info(f"[文档上传] 文件保存成功 - file_path: {file_path}, filename: {filename}")
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        logger.debug(f"[文档上传] 文件大小: {file_size} 字节")
        
        # 创建文档记录
        logger.debug(f"[文档上传] 开始创建文档记录 - filename: {filename}, original_filename: {file.filename}")
        document = document_service.create_document_record(
            meeting_id=meeting_id,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            user_id=user_id
        )
        logger.info(f"[文档上传] 文档记录创建成功 - document_id: {document.id}, file_type: {document.file_type}")
        
        # 如果是docx文件，尝试同步解析（如果失败则标记为失败状态）
        if document.file_type == 'docx':
            try:
                logger.info(f"[文档解析] 开始解析docx文档 - document_id: {document.id}, meeting_id: {meeting_id}")
                # 同步解析，如果失败会抛出异常
                parsed_document = document_service.parse_and_extract_document(document.id, meeting_id)
                logger.info(f"[文档解析] 文档解析完成 - document_id: {document.id}")
                
                # 重新获取文档以获取最新状态
                from models.document import Document
                document = Document.query.get(document.id)
                
                logger.info(f"[文档上传] 上传成功（解析完成） - document_id: {document.id}, meeting_id: {meeting_id}")
                # 重新获取文档以获取最新状态（包括解析内容）
                from models.document import Document
                completed_document = Document.query.get(document.id)
                return jsonify({
                    'success': True,
                    'data': completed_document.to_dict(include_content=True) if completed_document else document.to_dict(),
                    'message': '文档上传成功，解析完成'
                }), 200
            except Exception as e:
                logger.error(f"[文档解析] 解析文档失败 - document_id: {document.id}, 错误: {str(e)}", exc_info=True)
                
                # parse_and_extract_document 内部已经更新了文档状态为 'failed'
                # 重新获取文档以获取最新状态（包括错误信息）
                from models.document import Document
                failed_document = Document.query.get(document.id)
                
                # 返回错误响应
                return jsonify({
                    'success': False,
                    'message': f'文档上传成功，但解析失败: {str(e)}',
                    'data': failed_document.to_dict(include_content=True) if failed_document else document.to_dict()
                }), 200  # 返回200但success为False，让前端知道上传成功但解析失败
        
        logger.info(f"[文档上传] 上传成功 - document_id: {document.id}, meeting_id: {meeting_id}")
        return jsonify({
            'success': True,
            'data': document.to_dict(include_content=True),
            'message': '文档上传成功'
        }), 200
    
    except ValueError as e:
        logger.error(f"[文档上传] 参数错误 - meeting_id: {meeting_id}, 错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    
    except RequestEntityTooLarge:
        logger.error(f"[文档上传] 文件过大 - meeting_id: {meeting_id}")
        return jsonify({
            'success': False,
            'message': '文件大小超过限制（最大20MB）'
        }), 413
    
    except Exception as e:
        logger.error(f"[文档上传] 上传失败 - meeting_id: {meeting_id}, 错误类型: {type(e).__name__}, 错误: {str(e)}", exc_info=True)
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


@document_bp.route('/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """获取单个文档的详细信息（包含解析内容）"""
    try:
        user_id = get_jwt_identity()
        
        from models.document import Document
        document = Document.query.filter_by(id=document_id, user_id=user_id).first()
        
        if not document:
            return jsonify({
                'success': False,
                'message': '文档不存在或无权限'
            }), 404
        
        return jsonify({
            'success': True,
            'data': document.to_dict(include_content=True)
        }), 200
    
    except Exception as e:
        logger.error(f"[获取文档] 获取文档失败 - document_id: {document_id}, 错误: {str(e)}", exc_info=True)
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

