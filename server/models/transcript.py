"""
转写记录模型
"""
from datetime import datetime
from database import db
import json
from utils.datetime_utils import beijing_now


class Transcript(db.Model):
    """转写记录模型"""
    __tablename__ = 'transcripts'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.String(36), db.ForeignKey('meetings.id'), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)  # 转写文本
    summary = db.Column(db.Text, nullable=True)  # 摘要（JSON格式）
    key_points = db.Column(db.Text, nullable=True)  # 要点（JSON格式）
    duration = db.Column(db.Float, nullable=True)  # 时长（秒）
    created_at = db.Column(db.DateTime, default=beijing_now, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=beijing_now, onupdate=beijing_now, nullable=False)
    
    @property
    def summary_dict(self):
        """获取摘要字典"""
        if self.summary:
            try:
                return json.loads(self.summary)
            except:
                return None
        return None
    
    @summary_dict.setter
    def summary_dict(self, value):
        """设置摘要字典"""
        if value:
            self.summary = json.dumps(value, ensure_ascii=False)
        else:
            self.summary = None
    
    @property
    def key_points_list(self):
        """获取要点列表"""
        if self.key_points:
            try:
                return json.loads(self.key_points)
            except:
                return []
        return []
    
    @key_points_list.setter
    def key_points_list(self, value):
        """设置要点列表"""
        if value:
            self.key_points = json.dumps(value, ensure_ascii=False)
        else:
            self.key_points = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'text': self.text,
            'summary': self.summary_dict,
            'key_points': self.key_points_list,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Transcript {self.id}>'

