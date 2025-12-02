"""
会议服务
"""
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from database import db
from models.meeting import Meeting
from models.transcript import Transcript
from services.tytingwu_service import TyingWuService


class MeetingService:
    """会议服务类"""
    
    def __init__(self):
        self.tytingwu_service = TyingWuService()
    
    def create_meeting(self, meeting_name: str, user_id: int, description: Optional[str] = None, subject: Optional[str] = None, teacher_ids: Optional[List[int]] = None, host_teacher_id: Optional[int] = None, task_id: Optional[str] = None, stream_url: Optional[str] = None) -> Dict:
        """
        创建会议
        
        Args:
            meeting_name: 会议名称
            user_id: 用户ID
            description: 会议描述
            teacher_ids: 教师ID列表
            host_teacher_id: 主持人教师ID
            task_id: 任务ID（可选，如果提供则使用，否则不创建任务）
            stream_url: WebSocket URL（可选，如果提供则使用）
        
        Returns:
            会议信息
        """
        meeting_id = str(uuid.uuid4())
        
        # 创建会议记录（任务信息稍后通过update_meeting_task更新）
        meeting = Meeting(
            id=meeting_id,
            name=meeting_name,
            description=description,
            subject=subject,
            status='pending',  # 初始状态为pending，等待任务创建
            task_id=task_id,
            stream_url=stream_url,
            user_id=user_id
        )
        
        db.session.add(meeting)
        db.session.flush()  # 获取meeting.id
        
        # 保存会议和教师的关联关系
        if teacher_ids:
            from models.meeting_teacher import MeetingTeacher
            from models.teacher import Teacher
            
            for teacher_id in teacher_ids:
                # 验证教师是否存在
                teacher = Teacher.query.get(teacher_id)
                if not teacher:
                    import logging
                    logging.warning(f"教师不存在: {teacher_id}")
                    continue
                
                # 判断是否是主持人
                is_host = (host_teacher_id is not None and teacher_id == host_teacher_id)
                
                meeting_teacher = MeetingTeacher(
                    meeting_id=meeting.id,
                    teacher_id=teacher_id,
                    is_host=is_host
                )
                db.session.add(meeting_teacher)
        
        db.session.commit()
        
        return meeting.to_dict(include_teachers=True)
    
    def get_meeting(self, meeting_id: str, user_id: Optional[int] = None) -> Optional[Dict]:
        """
        获取会议信息
        
        Args:
            meeting_id: 会议ID
            user_id: 用户ID（用于权限检查）
        
        Returns:
            会议信息
        """
        query = Meeting.query.filter_by(id=meeting_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        meeting = query.first()
        if not meeting:
            return None
        
        # 自动修复状态：如果会议有任务信息但状态是pending，自动更新为running
        if meeting.status == 'pending' and meeting.task_id and meeting.stream_url:
            meeting.status = 'running'
            db.session.commit()
        
        return meeting.to_dict(include_transcripts=True, include_teachers=True)
    
    def list_meetings(self, user_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict]:
        """
        列出所有会议
        
        Args:
            user_id: 用户ID（可选，用于筛选）
            status: 状态筛选（可选）
        
        Returns:
            会议列表
        """
        query = Meeting.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        
        meetings = query.order_by(Meeting.created_at.desc()).all()
        
        # 自动修复状态：如果会议有任务信息但状态是pending，自动更新为running
        updated = False
        for meeting in meetings:
            if meeting.status == 'pending' and meeting.task_id and meeting.stream_url:
                meeting.status = 'running'
                updated = True
        
        if updated:
            db.session.commit()
        
        # 包含教师信息以便前端显示科目和数量
        return [m.to_dict(include_teachers=True) for m in meetings]
    
    def update_meeting_task(self, meeting_id: str, task_id: str, stream_url: str, user_id: Optional[int] = None) -> Dict:
        """
        更新会议的任务信息
        
        Args:
            meeting_id: 会议ID
            task_id: 任务ID
            stream_url: WebSocket URL
            user_id: 用户ID（用于权限检查）
        
        Returns:
            更新后的会议信息
        """
        query = Meeting.query.filter_by(id=meeting_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        meeting = query.first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        meeting.task_id = task_id
        meeting.stream_url = stream_url
        meeting.status = 'running'  # 更新状态为running
        db.session.commit()
        
        return meeting.to_dict(include_teachers=True)
    
    def stop_meeting(self, meeting_id: str, user_id: Optional[int] = None) -> Dict:
        """
        停止会议（结束实时记录）
        
        当会议结束时，会调用结束实时记录API。
        如果开启了摘要、要点提炼等功能，任务状态会变为ONGOING，表示正在后处理。
        
        Args:
            meeting_id: 会议ID
            user_id: 用户ID（用于权限检查）
        
        Returns:
            更新后的会议信息
        """
        import logging
        
        query = Meeting.query.filter_by(id=meeting_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        meeting = query.first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        if meeting.status == 'stopped':
            return meeting.to_dict()
        
        # 停止通义听悟任务（结束实时记录）
        try:
            if meeting.task_id:
                logging.info(f"结束实时记录: TaskId={meeting.task_id}")
                stop_result = self.tytingwu_service.stop_task(meeting.task_id)
                
                # 检查停止结果
                if stop_result.get('Code') == '0':
                    task_status = stop_result.get('Data', {}).get('TaskStatus', '')
                    logging.info(f"实时记录已结束，任务状态: {task_status}")
                    
                    # 如果任务状态是ONGOING，说明正在后处理（摘要、要点提炼等）
                    if task_status == 'ONGOING':
                        logging.info("任务进入后处理阶段，摘要和要点提炼功能正在处理中")
                else:
                    logging.warning(f"结束实时记录失败: {stop_result.get('Message', '未知错误')}")
        except Exception as e:
            logging.warning(f"停止任务失败: {str(e)}")
            # 即使停止失败也更新状态
        
        meeting.status = 'stopped'
        db.session.commit()
        
        return meeting.to_dict(include_teachers=True)
    
    def complete_meeting(self, meeting_id: str, user_id: Optional[int] = None) -> Dict:
        """
        完成会议（将状态设置为 completed）
        
        会议结束时，会调用结束实时记录API，然后进入后处理阶段。
        如果开启了摘要、要点提炼等功能，任务状态会变为ONGOING，表示正在后处理。
        
        Args:
            meeting_id: 会议ID
            user_id: 用户ID（用于权限检查）
        
        Returns:
            更新后的会议信息
        """
        import logging
        
        query = Meeting.query.filter_by(id=meeting_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        meeting = query.first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        if meeting.status == 'completed':
            return meeting.to_dict()
        
        # 如果会议还在运行，先停止通义听悟任务（结束实时记录）
        if meeting.status == 'running':
            try:
                if meeting.task_id:
                    logging.info(f"结束实时记录: TaskId={meeting.task_id}")
                    stop_result = self.tytingwu_service.stop_task(meeting.task_id)
                    
                    # 检查停止结果
                    if stop_result.get('Code') == '0':
                        task_status = stop_result.get('Data', {}).get('TaskStatus', '')
                        logging.info(f"实时记录已结束，任务状态: {task_status}")
                        
                        # 如果任务状态是ONGOING，说明正在后处理（摘要、要点提炼等）
                        # 此时可以尝试获取结果，但可能需要等待一段时间
                        if task_status == 'ONGOING':
                            logging.info("任务进入后处理阶段，摘要和要点提炼功能正在处理中")
                    else:
                        logging.warning(f"结束实时记录失败: {stop_result.get('Message', '未知错误')}")
            except Exception as e:
                logging.warning(f"停止任务失败: {str(e)}")
        
        meeting.status = 'completed'
        db.session.commit()
        
        return meeting.to_dict(include_teachers=True)
    
    def delete_meeting(self, meeting_id: str, user_id: Optional[int] = None) -> None:
        """
        删除会议
        
        Args:
            meeting_id: 会议ID
            user_id: 用户ID（用于权限检查）
        
        Raises:
            ValueError: 会议不存在
        """
        from models.document import Document
        import os
        import logging
        
        query = Meeting.query.filter_by(id=meeting_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        meeting = query.first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        # 停止通义听悟任务（如果还在运行）
        try:
            if meeting.task_id and meeting.status == 'running':
                self.tytingwu_service.stop_task(meeting.task_id)
        except Exception as e:
            logging.warning(f"停止任务失败: {str(e)}")
        
        # 删除关联的会议-教师关联记录
        from models.meeting_teacher import MeetingTeacher
        meeting_teachers = MeetingTeacher.query.filter_by(meeting_id=meeting_id).all()
        for mt in meeting_teachers:
            db.session.delete(mt)
        
        # 删除关联的文档记录和文件
        documents = Document.query.filter_by(meeting_id=meeting_id).all()
        for doc in documents:
            # 删除物理文件
            try:
                if doc.file_path and os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
                    logging.info(f"已删除文件: {doc.file_path}")
            except Exception as e:
                logging.warning(f"删除文件失败: {doc.file_path}, 错误: {str(e)}")
            
            # 删除数据库记录
            db.session.delete(doc)
        
        # 删除会议（级联删除 transcripts）
        db.session.delete(meeting)
        db.session.commit()
        
        logging.info(f"会议已删除: {meeting_id}")
    
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
        
        return meeting.to_dict(include_transcripts=True)
    
    def append_message(self, meeting_id: str, message: Dict) -> Dict:
        """
        追加单条消息到转写记录（JSONL格式）
        
        Args:
            meeting_id: 会议ID
            message: 消息字典，包含 name, time, type, content
        
        Returns:
            更新后的会议信息
        """
        import json
        
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
            # 创建新的转写记录
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
        
        return meeting.to_dict(include_transcripts=True)
    
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
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'从任务数据中提取摘要: summarization={bool(summarization)}, meeting_assistance={bool(meeting_assistance)}')
        if summarization:
            logger.info(f'摘要数据结构: {list(summarization.keys())}')
        if meeting_assistance:
            logger.info(f'要点提炼数据结构: {list(meeting_assistance.keys())}')
        
        if not summarization and not meeting_assistance:
            raise ValueError("任务未包含摘要或要点提炼结果，请确保创建任务时启用了相关功能")
        
        # 解析摘要结果
        summary_result = {
            'paragraph_summary': summarization.get('ParagraphSummary', '') if summarization else '',  # 全文摘要
            'paragraph_title': summarization.get('ParagraphTitle', '') if summarization else '',  # 全文摘要标题
            'conversational_summary': summarization.get('ConversationalSummary', []) if summarization else [],  # 发言总结
            'questions_answering_summary': summarization.get('QuestionsAnsweringSummary', []) if summarization else [],  # 问答回顾
            'mind_map_summary': summarization.get('MindMapSummary', []) if summarization else [],  # 思维导图
        }
        
        # 解析要点提炼结果
        if meeting_assistance:
            summary_result['meeting_assistance'] = {
                'keywords': meeting_assistance.get('Keywords', []),  # 关键词
                'key_sentences': meeting_assistance.get('KeySentences', []),  # 重点内容（关键句）
                'actions': meeting_assistance.get('Actions', []),  # 待办事项
            }
        else:
            summary_result['meeting_assistance'] = {
                'keywords': [],
                'key_sentences': [],
                'actions': [],
            }
        
        logger.info(f'解析后的摘要结果: paragraph_summary长度={len(summary_result["paragraph_summary"])}, conversational_summary数量={len(summary_result["conversational_summary"])}, keywords数量={len(summary_result["meeting_assistance"]["keywords"])}')
        
        # 获取或创建转写记录
        transcript_record = Transcript.query.filter_by(meeting_id=meeting_id).order_by(
            Transcript.created_at.desc()
        ).first()
        
        if not transcript_record:
            # 如果没有转写记录，创建一个
            # 尝试从任务数据中获取转写文本
            transcription_text = ''
            if task_data.get('Transcription'):
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
        
        # 更新转写记录的摘要（包含摘要和要点提炼结果）
        transcript_record.summary_dict = summary_result
        db.session.commit()
        
        return meeting.to_dict(include_transcripts=True)
    
    def save_summary_from_task_data(self, meeting_id: str, task_data: Dict) -> Dict:
        """
        从任务数据中保存摘要结果
        
        Args:
            meeting_id: 会议ID
            task_data: 任务数据（包含 Summarization 和 MeetingAssistance）
        
        Returns:
            更新后的会议信息
        """
        import logging
        logger = logging.getLogger(__name__)
        
        meeting = Meeting.query.filter_by(id=meeting_id).first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        summarization = task_data.get('Summarization', {})
        meeting_assistance = task_data.get('MeetingAssistance', {})
        
        # 解析摘要结果
        summary_result = {
            'paragraph_summary': summarization.get('ParagraphSummary', '') if summarization else '',
            'paragraph_title': summarization.get('ParagraphTitle', '') if summarization else '',
            'conversational_summary': summarization.get('ConversationalSummary', []) if summarization else [],
            'questions_answering_summary': summarization.get('QuestionsAnsweringSummary', []) if summarization else [],
            'mind_map_summary': summarization.get('MindMapSummary', []) if summarization else [],
            'mp3_url': task_data.get('mp3_url') or task_data.get('OutputMp3Path'),  # 保存 MP3 URL
        }
        
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
        
        # 更新转写记录的摘要
        transcript_record.summary_dict = summary_result
        db.session.commit()
        
        return meeting.to_dict(include_transcripts=True)
    
    # download_and_save_mp3 方法已删除，不再需要下载保存 MP3 文件
    # 直接使用 OutputMp3Path URL 即可
    
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
        
        return meeting.to_dict(include_transcripts=True)

