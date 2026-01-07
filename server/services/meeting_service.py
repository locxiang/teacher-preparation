"""
会议核心服务
处理会议的基本 CRUD 操作和状态管理
"""
import uuid
import logging
from typing import Dict, Optional, List
from database import db
from models.meeting import Meeting
from models.meeting_teacher import MeetingTeacher
from services.tytingwu_service import TyingWuService

logger = logging.getLogger(__name__)


class MeetingService:
    """会议服务类 - 核心CRUD操作"""
    
    def __init__(self):
        self.tytingwu_service = TyingWuService()
    
    def create_meeting(
        self,
        meeting_name: str,
        user_id: int,
        description: Optional[str] = None,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        lesson_type: Optional[str] = None,
        teacher_ids: Optional[List[int]] = None,
        host_teacher_id: Optional[int] = None,
        task_id: Optional[str] = None,
        stream_url: Optional[str] = None
    ) -> Dict:
        """
        创建会议
        
        Args:
            meeting_name: 会议名称
            user_id: 用户ID
            description: 会议描述
            subject: 学科
            grade: 年级
            lesson_type: 备课类型（新课、复习、专题等）
            teacher_ids: 教师ID列表
            host_teacher_id: 主持人教师ID
            task_id: 任务ID（可选，如果提供则使用，否则不创建任务）
            stream_url: WebSocket URL（可选，如果提供则使用）
        
        Returns:
            会议信息
        """
        meeting_id = str(uuid.uuid4())
        
        # 创建会议记录
        meeting = Meeting(
            id=meeting_id,
            name=meeting_name,
            description=description,
            subject=subject,
            grade=grade,
            lesson_type=lesson_type,
            status='pending',  # 初始状态为pending，等待任务创建
            task_id=task_id,
            stream_url=stream_url,
            user_id=user_id
        )
        
        db.session.add(meeting)
        db.session.flush()  # 获取meeting.id
        
        # 保存会议和教师的关联关系
        if teacher_ids:
            from models.teacher import Teacher
            
            for teacher_id in teacher_ids:
                # 验证教师是否存在
                teacher = Teacher.query.get(teacher_id)
                if not teacher:
                    logger.warning(f"教师不存在: {teacher_id}")
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
    
    def update_meeting_task(
        self,
        meeting_id: str,
        task_id: str,
        stream_url: str,
        user_id: Optional[int] = None
    ) -> Dict:
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
        query = Meeting.query.filter_by(id=meeting_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        meeting = query.first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        if meeting.status == 'stopped':
            return meeting.to_dict(include_teachers=True)
        
        # 停止通义听悟任务（结束实时记录）
        try:
            if meeting.task_id:
                logger.info(f"结束实时记录: TaskId={meeting.task_id}")
                stop_result = self.tytingwu_service.stop_task(meeting.task_id)
                
                # 检查停止结果
                if stop_result.get('Code') == '0':
                    task_status = stop_result.get('Data', {}).get('TaskStatus', '')
                    logger.info(f"实时记录已结束，任务状态: {task_status}")
                    
                    # 如果任务状态是ONGOING，说明正在后处理（摘要、要点提炼等）
                    if task_status == 'ONGOING':
                        logger.info("任务进入后处理阶段，摘要和要点提炼功能正在处理中")
                else:
                    logger.warning(f"结束实时记录失败: {stop_result.get('Message', '未知错误')}")
        except Exception as e:
            logger.warning(f"停止任务失败: {str(e)}")
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
        query = Meeting.query.filter_by(id=meeting_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        meeting = query.first()
        if not meeting:
            raise ValueError(f"会议不存在: {meeting_id}")
        
        if meeting.status == 'completed':
            return meeting.to_dict(include_teachers=True)
        
        # 如果会议还在运行，先停止通义听悟任务（结束实时记录）
        if meeting.status == 'running':
            try:
                if meeting.task_id:
                    logger.info(f"结束实时记录: TaskId={meeting.task_id}")
                    stop_result = self.tytingwu_service.stop_task(meeting.task_id)
                    
                    # 检查停止结果
                    if stop_result.get('Code') == '0':
                        task_status = stop_result.get('Data', {}).get('TaskStatus', '')
                        logger.info(f"实时记录已结束，任务状态: {task_status}")
                        
                        # 如果任务状态是ONGOING，说明正在后处理（摘要、要点提炼等）
                        if task_status == 'ONGOING':
                            logger.info("任务进入后处理阶段，摘要和要点提炼功能正在处理中")
                    else:
                        logger.warning(f"结束实时记录失败: {stop_result.get('Message', '未知错误')}")
            except Exception as e:
                logger.warning(f"停止任务失败: {str(e)}")
        
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
            logger.warning(f"停止任务失败: {str(e)}")
        
        # 删除关联的会议-教师关联记录
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
                    logger.info(f"已删除文件: {doc.file_path}")
            except Exception as e:
                logger.warning(f"删除文件失败: {doc.file_path}, 错误: {str(e)}")
            
            # 删除数据库记录
            db.session.delete(doc)
        
        # 删除会议（级联删除 transcripts）
        db.session.delete(meeting)
        db.session.commit()
        
        logger.info(f"会议已删除: {meeting_id}")
