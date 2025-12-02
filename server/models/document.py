"""
文档模型
"""
from datetime import datetime
from database import db


class Document(db.Model):
    """文档模型"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.String(36), db.ForeignKey('meetings.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    file_path = db.Column(db.String(500), nullable=False)  # 文件存储路径
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小（字节）
    file_type = db.Column(db.String(50), nullable=False)  # 文件类型：pdf, docx, pptx, txt等
    mime_type = db.Column(db.String(100), nullable=True)  # MIME类型
    status = db.Column(db.String(20), default='uploaded', nullable=False)  # uploaded, processing, completed, failed
    parsed_content = db.Column(db.Text, nullable=True)  # 解析后的文本内容
    parse_progress = db.Column(db.Integer, default=0, nullable=False)  # 解析进度 0-100
    error_message = db.Column(db.Text, nullable=True)  # 错误信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_size_mb': round(self.file_size / (1024 * 1024), 2),
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'status': self.status,
            'parse_progress': self.parse_progress,
            'error_message': self.error_message,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'

