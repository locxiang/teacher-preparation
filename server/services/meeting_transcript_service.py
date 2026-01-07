"""
会议转写服务
"""
import json
from typing import Dict
from database import db
from models.meeting import Meeting
from models.transcript import Transcript


class MeetingTranscriptService:
    """会议转写服务类"""
    
    def update_transcript(self, meeting_id: str, transcript: str) -> Dict:
        """
        更新转写文本（旧接口，保持兼容）
        
        Args:
            meeting_id: 会议ID
            transcript: 转写文本
        
        Returns:
            更新后的会议信息
        """
        meeting = Meeting.query.filter_by(id=meeting_id).first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        # 创建或更新转写记录
        transcript_record = Transcript.query.filter_by(meeting_id=meeting_id).order_by(
            Transcript.created_at.desc()
        ).first()
        
        if transcript_record:
            transcript_record.text = transcript
        else:
            transcript_record = Transcript(
                meeting_id=meeting_id,
                text=transcript
            )
            db.session.add(transcript_record)
        
        db.session.commit()
        
        return meeting.to_dict(include_transcripts=True, include_teachers=True)
    
    def append_message(self, meeting_id: str, message: Dict) -> Dict:
        """
        追加单条消息到转写记录（JSONL格式）
        
        Args:
            meeting_id: 会议ID
            message: 消息字典，包含 name, time, type, content
        
        Returns:
            更新后的会议信息
        """
        meeting = Meeting.query.filter_by(id=meeting_id).first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        # 验证消息格式
        required_fields = ['name', 'time', 'type', 'content']
        for field in required_fields:
            if field not in message:
                raise ValueError(f"消息缺少必需字段: {field}")
        
        # 获取或创建转写记录
        transcript_record = Transcript.query.filter_by(meeting_id=meeting_id).order_by(
            Transcript.created_at.desc()
        ).first()
        
        if not transcript_record:
            transcript_record = Transcript(
                meeting_id=meeting_id,
                text=''
            )
            db.session.add(transcript_record)
        
        # 将消息转换为 JSON 字符串（单行，类似 JSONL 格式）
        message_json = json.dumps(message, ensure_ascii=False)
        
        # 追加到现有文本（每行一条 JSON）
        if transcript_record.text:
            transcript_record.text += '\n' + message_json
        else:
            transcript_record.text = message_json
        
        db.session.commit()
        
        return meeting.to_dict(include_transcripts=True, include_teachers=True)

