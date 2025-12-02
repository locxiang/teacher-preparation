"""
文档处理服务
"""
import os
import uuid
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
import logging
from database import db
from models.document import Document

logger = logging.getLogger(__name__)

# 允许的文档格式
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md', 'xls', 'xlsx'}

# 文档文件存储目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'documents')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 文件类型映射
FILE_TYPE_MAP = {
    'pdf': 'pdf',
    'doc': 'doc',
    'docx': 'docx',
    'ppt': 'ppt',
    'pptx': 'pptx',
    'txt': 'txt',
    'md': 'txt',
    'xls': 'xls',
    'xlsx': 'xlsx',
}

# MIME类型映射
MIME_TYPE_MAP = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'txt': 'text/plain',
    'md': 'text/markdown',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}


class DocumentService:
    """文档处理服务类"""
    
    def __init__(self):
        self.upload_folder = UPLOAD_FOLDER
    
    def allowed_file(self, filename: str) -> bool:
        """检查文件格式是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def get_file_type(self, filename: str) -> str:
        """获取文件类型"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return FILE_TYPE_MAP.get(ext, 'unknown')
    
    def get_mime_type(self, filename: str) -> str:
        """获取MIME类型"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return MIME_TYPE_MAP.get(ext, 'application/octet-stream')
    
    def save_document_file(self, file, meeting_id: str) -> Tuple[str, str]:
        """
        保存文档文件
        
        Args:
            file: 上传的文件对象
            meeting_id: 会议ID
        
        Returns:
            (文件路径, 文件名) 元组
        """
        if not file or not file.filename:
            raise ValueError("文件不能为空")
        
        if not self.allowed_file(file.filename):
            raise ValueError(f"不支持的文档格式。支持的格式: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # 生成安全的文件名
        original_filename = file.filename
        filename = secure_filename(original_filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{meeting_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # 创建会议目录
        meeting_folder = os.path.join(self.upload_folder, meeting_id)
        os.makedirs(meeting_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(meeting_folder, unique_filename)
        file.save(file_path)
        
        logger.info(f"文档文件已保存: {file_path}")
        
        return file_path, unique_filename
    
    def create_document_record(
        self,
        meeting_id: str,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        user_id: int
    ) -> Document:
        """
        创建文档记录
        
        Args:
            meeting_id: 会议ID
            filename: 存储的文件名
            original_filename: 原始文件名
            file_path: 文件路径
            file_size: 文件大小（字节）
            user_id: 用户ID
        
        Returns:
            Document对象
        """
        document = Document(
            meeting_id=meeting_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=self.get_file_type(original_filename),
            mime_type=self.get_mime_type(original_filename),
            status='uploaded',
            user_id=user_id
        )
        
        db.session.add(document)
        db.session.commit()
        
        logger.info(f"文档记录已创建: {document.id}")
        
        return document
    
    def get_documents_by_meeting(self, meeting_id: str, user_id: Optional[int] = None) -> list:
        """
        获取会议的所有文档
        
        Args:
            meeting_id: 会议ID
            user_id: 用户ID（可选，用于权限检查）
        
        Returns:
            文档列表
        """
        query = Document.query.filter_by(meeting_id=meeting_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        documents = query.order_by(Document.created_at.desc()).all()
        return [doc.to_dict() for doc in documents]
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """
        删除文档
        
        Args:
            document_id: 文档ID
            user_id: 用户ID（用于权限检查）
        
        Returns:
            是否删除成功
        """
        document = Document.query.filter_by(
            id=document_id,
            user_id=user_id
        ).first()
        
        if not document:
            return False
        
        # 删除文件
        if os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                logger.warning(f"删除文件失败: {e}")
        
        # 删除数据库记录
        db.session.delete(document)
        db.session.commit()
        
        logger.info(f"文档已删除: {document_id}")
        
        return True
    
    def update_document_status(
        self,
        document_id: int,
        status: str,
        parse_progress: Optional[int] = None,
        parsed_content: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """
        更新文档状态
        
        Args:
            document_id: 文档ID
            status: 状态
            parse_progress: 解析进度（0-100）
            parsed_content: 解析后的内容
            error_message: 错误信息
        
        Returns:
            Document对象
        """
        document = Document.query.get(document_id)
        if not document:
            return None
        
        document.status = status
        if parse_progress is not None:
            document.parse_progress = parse_progress
        if parsed_content is not None:
            document.parsed_content = parsed_content
        if error_message is not None:
            document.error_message = error_message
        
        db.session.commit()
        
        return document

