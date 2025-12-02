"""
教师服务
"""
from typing import List, Dict, Optional
from database import db
from models.teacher import Teacher


class TeacherService:
    """教师服务类"""
    
    def list_teachers(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        获取教师列表
        
        Args:
            user_id: 用户ID（可选，用于筛选）
        
        Returns:
            教师列表
        """
        query = Teacher.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        teachers = query.order_by(Teacher.created_at.desc()).all()
        return [t.to_dict() for t in teachers]
    
    def create_teacher(
        self,
        name: str,
        subject: str,
        user_id: int,
        feature_id: Optional[str] = None
    ) -> Dict:
        """
        创建教师
        
        Args:
            name: 教师姓名
            subject: 学科
            user_id: 用户ID
            feature_id: 声纹特征ID（可选）
        
        Returns:
            教师信息
        """
        # 检查同一用户下是否已有同名教师
        existing = Teacher.query.filter_by(
            name=name,
            user_id=user_id
        ).first()
        
        if existing:
            raise ValueError(f"教师 {name} 已存在")
        
        teacher = Teacher(
            name=name,
            subject=subject,
            feature_id=feature_id,
            user_id=user_id
        )
        
        db.session.add(teacher)
        db.session.commit()
        
        return teacher.to_dict()
    
    def update_teacher(
        self,
        teacher_id: int,
        user_id: int,
        name: Optional[str] = None,
        subject: Optional[str] = None,
        feature_id: Optional[str] = None
    ) -> Dict:
        """
        更新教师信息
        
        Args:
            teacher_id: 教师ID
            user_id: 用户ID（用于权限检查）
            name: 教师姓名（可选）
            subject: 学科（可选）
            feature_id: 声纹特征ID（可选）
        
        Returns:
            更新后的教师信息
        """
        teacher = Teacher.query.filter_by(
            id=teacher_id,
            user_id=user_id
        ).first()
        
        if not teacher:
            raise ValueError(f"教师不存在或无权限")
        
        if name is not None:
            teacher.name = name
        if subject is not None:
            teacher.subject = subject
        if feature_id is not None:
            teacher.feature_id = feature_id
        
        db.session.commit()
        
        return teacher.to_dict()
    
    def delete_teacher(self, teacher_id: int, user_id: int) -> None:
        """
        删除教师
        
        Args:
            teacher_id: 教师ID
            user_id: 用户ID（用于权限检查）
        """
        teacher = Teacher.query.filter_by(
            id=teacher_id,
            user_id=user_id
        ).first()
        
        if not teacher:
            raise ValueError(f"教师不存在或无权限")
        
        db.session.delete(teacher)
        db.session.commit()
    
    def get_teacher(self, teacher_id: int, user_id: Optional[int] = None) -> Optional[Dict]:
        """
        获取教师信息
        
        Args:
            teacher_id: 教师ID
            user_id: 用户ID（可选，用于权限检查）
        
        Returns:
            教师信息
        """
        query = Teacher.query.filter_by(id=teacher_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        teacher = query.first()
        return teacher.to_dict() if teacher else None

