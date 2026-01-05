"""
教师模型
"""
from datetime import datetime
from database import db
from utils.datetime_utils import beijing_now


class Teacher(db.Model):
    """教师模型"""
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False)  # 学科：数学、语文等
    feature_id = db.Column(db.String(100), nullable=True)  # 声纹特征ID（可选）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 创建者ID
    created_at = db.Column(db.DateTime, default=beijing_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=beijing_now, onupdate=beijing_now, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'feature_id': self.feature_id,
            'has_voiceprint': bool(self.feature_id),
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Teacher {self.name} ({self.subject})>'

