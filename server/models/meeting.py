"""
会议模型
"""
from datetime import datetime
from database import db


class Meeting(db.Model):
    """会议模型"""
    __tablename__ = 'meetings'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(50), nullable=True)  # 学科：数学、语文等
    grade = db.Column(db.String(50), nullable=True)  # 年级：初一年级、初二年级等
    lesson_type = db.Column(db.String(50), nullable=True)  # 备课类型：新课、复习、专题等
    status = db.Column(db.String(20), default='running', nullable=False, index=True)  # running, stopped, completed
    task_id = db.Column(db.String(100), nullable=True)  # 通义听悟任务ID
    stream_url = db.Column(db.String(500), nullable=True)  # 推流URL
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    transcripts = db.relationship('Transcript', backref='meeting', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='meeting', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_transcripts=False, include_teachers=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject': self.subject,
            'grade': self.grade,
            'lesson_type': self.lesson_type,
            'status': self.status,
            'task_id': self.task_id,
            'stream_url': self.stream_url,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'summary': None,
            'key_points': []
        }
        
        if include_transcripts:
            data['transcripts'] = [t.to_dict() for t in self.transcripts]
            # 获取最新转写文本
            if self.transcripts:
                latest_transcript = max(self.transcripts, key=lambda x: x.created_at)
                data['transcript'] = latest_transcript.text
                # 使用 summary_dict 属性返回解析后的字典，而不是字符串
                data['summary'] = latest_transcript.summary_dict
                # 使用 key_points_list 属性返回解析后的列表，而不是字符串
                data['key_points'] = latest_transcript.key_points_list
        
        if include_teachers:
            # 包含参与的老师信息
            teachers_data = []
            host_teacher = None
            for mt in self.meeting_teachers:
                teacher_data = mt.teacher.to_dict() if mt.teacher else None
                if teacher_data:
                    teacher_data['is_host'] = mt.is_host
                    teachers_data.append(teacher_data)
                    if mt.is_host:
                        host_teacher = teacher_data
            data['teachers'] = teachers_data
            data['host_teacher'] = host_teacher
        
        return data
    
    def __repr__(self):
        return f'<Meeting {self.name}>'

