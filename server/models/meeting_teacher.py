"""
会议-教师关联模型
"""
from datetime import datetime
from database import db
from utils.datetime_utils import beijing_now


class MeetingTeacher(db.Model):
    """会议-教师关联模型"""
    __tablename__ = 'meeting_teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.String(36), db.ForeignKey('meetings.id'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False, index=True)
    is_host = db.Column(db.Boolean, default=False, nullable=False)  # 是否是主持人
    created_at = db.Column(db.DateTime, default=beijing_now, nullable=False)
    
    # 关系
    meeting = db.relationship('Meeting', backref='meeting_teachers')
    teacher = db.relationship('Teacher', backref='meeting_teachers')
    
    # 唯一约束：一个会议中，一个教师只能出现一次
    __table_args__ = (
        db.UniqueConstraint('meeting_id', 'teacher_id', name='uq_meeting_teacher'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'teacher_id': self.teacher_id,
            'is_host': self.is_host,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<MeetingTeacher meeting_id={self.meeting_id} teacher_id={self.teacher_id} is_host={self.is_host}>'

