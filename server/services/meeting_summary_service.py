"""
会议摘要服务
"""
import logging
from typing import Dict
from database import db
from models.meeting import Meeting
from models.transcript import Transcript
from services.tytingwu_service import TyingWuService

logger = logging.getLogger(__name__)


class MeetingSummaryService:
    """会议摘要服务类"""
    
    def __init__(self):
        self.tytingwu_service = TyingWuService()
    
    def generate_summary(self, meeting_id: str, summary_type: str = 'brief') -> Dict:
        """
        生成会议摘要（通过查询任务信息获取摘要结果）
        
        参考文档：https://help.aliyun.com/zh/tingwu/large-model-summary
        
        Args:
            meeting_id: 会议ID
            summary_type: 摘要类型（'brief' 或 'detailed'，实际从任务信息中获取）
        
        Returns:
            更新后的会议信息
        """
        meeting = Meeting.query.filter_by(id=meeting_id).first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        if not meeting.task_id:
            raise ValueError("会议没有关联的通义听悟任务，无法获取摘要")
        
        # 查询任务信息（包含摘要结果）
        task_info = self.tytingwu_service.get_task_info(meeting.task_id)
        
        if task_info.get('Code') != '0':
            raise ValueError(f"查询任务信息失败: {task_info.get('Message', '未知错误')}")
        
        task_data = task_info.get('Data', {})
        summarization = task_data.get('Summarization', {})
        meeting_assistance = task_data.get('MeetingAssistance', {})
        
        logger.info(f'从任务数据中提取摘要: summarization={bool(summarization)}, meeting_assistance={bool(meeting_assistance)}')
        
        if not summarization and not meeting_assistance:
            raise ValueError("任务未包含摘要或要点提炼结果，请确保创建任务时启用了相关功能")
        
        # 解析摘要结果
        summary_result = self._parse_summary_result(summarization, meeting_assistance, task_data)
        
        # 保存摘要结果
        self._save_summary_to_transcript(meeting_id, summary_result, task_data)
        
        return meeting.to_dict(include_transcripts=True, include_teachers=True)
    
    def save_summary_from_task_data(self, meeting_id: str, task_data: Dict) -> Dict:
        """
        从任务数据中保存摘要结果
        
        Args:
            meeting_id: 会议ID
            task_data: 任务数据（包含 Summarization 和 MeetingAssistance）
        
        Returns:
            更新后的会议信息
        """
        meeting = Meeting.query.filter_by(id=meeting_id).first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        summarization = task_data.get('Summarization', {})
        meeting_assistance = task_data.get('MeetingAssistance', {})
        
        # 解析摘要结果
        summary_result = self._parse_summary_result(summarization, meeting_assistance, task_data)
        
        # 保存摘要结果
        self._save_summary_to_transcript(meeting_id, summary_result)
        
        return meeting.to_dict(include_transcripts=True, include_teachers=True)
    
    def extract_key_points(self, meeting_id: str) -> Dict:
        """
        提取会议要点
        
        Args:
            meeting_id: 会议ID
        
        Returns:
            更新后的会议信息
        """
        meeting = Meeting.query.filter_by(id=meeting_id).first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        # 获取最新转写文本
        transcript_record = Transcript.query.filter_by(meeting_id=meeting_id).order_by(
            Transcript.created_at.desc()
        ).first()
        
        if not transcript_record or not transcript_record.text:
            raise ValueError("会议转写文本为空，无法提取要点")
        
        # 提取要点
        key_points = self.tytingwu_service.extract_key_points(transcript_record.text)
        
        # 更新转写记录的要点
        transcript_record.key_points_list = key_points
        db.session.commit()
        
        return meeting.to_dict(include_transcripts=True, include_teachers=True)
    
    def _parse_summary_result(self, summarization: Dict, meeting_assistance: Dict, task_data: Dict = None) -> Dict:
        """解析摘要结果"""
        summary_result = {
            'paragraph_summary': summarization.get('ParagraphSummary', '') if summarization else '',
            'paragraph_title': summarization.get('ParagraphTitle', '') if summarization else '',
            'conversational_summary': summarization.get('ConversationalSummary', []) if summarization else [],
            'questions_answering_summary': summarization.get('QuestionsAnsweringSummary', []) if summarization else [],
            'mind_map_summary': summarization.get('MindMapSummary', []) if summarization else [],
        }
        
        # 添加 MP3 URL（如果存在）
        if task_data:
            summary_result['mp3_url'] = task_data.get('mp3_url') or task_data.get('OutputMp3Path')
        
        # 解析要点提炼结果
        if meeting_assistance:
            summary_result['meeting_assistance'] = {
                'keywords': meeting_assistance.get('Keywords', []),
                'key_sentences': meeting_assistance.get('KeySentences', []),
                'actions': meeting_assistance.get('Actions', []),
            }
        else:
            summary_result['meeting_assistance'] = {
                'keywords': [],
                'key_sentences': [],
                'actions': [],
            }
        
        logger.info(f'解析后的摘要结果: paragraph_summary长度={len(summary_result["paragraph_summary"])}, '
                   f'conversational_summary数量={len(summary_result["conversational_summary"])}, '
                   f'keywords数量={len(summary_result["meeting_assistance"]["keywords"])}')
        
        return summary_result
    
    def _save_summary_to_transcript(self, meeting_id: str, summary_result: Dict, task_data: Dict = None):
        """保存摘要结果到转写记录"""
        transcript_record = Transcript.query.filter_by(meeting_id=meeting_id).order_by(
            Transcript.created_at.desc()
        ).first()
        
        if not transcript_record:
            # 如果没有转写记录，创建一个
            transcription_text = ''
            if task_data and task_data.get('Transcription'):
                # 如果 Transcription 是 URL，需要下载
                if isinstance(task_data.get('Transcription'), str) and task_data.get('Transcription').startswith('http'):
                    transcription_text = f'转写文本URL: {task_data.get("Transcription")}'
                elif isinstance(task_data.get('Transcription'), dict):
                    transcription_text = task_data.get('Transcription', {}).get('Text', '') or ''
            
            transcript_record = Transcript(
                meeting_id=meeting_id,
                text=transcription_text
            )
            db.session.add(transcript_record)
        
        # 更新转写记录的摘要
        transcript_record.summary_dict = summary_result
        db.session.commit()

