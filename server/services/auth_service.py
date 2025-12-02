"""
用户认证服务
"""
from typing import Optional, Dict
from database import db
from models.user import User
from flask_jwt_extended import create_access_token


class AuthService:
    """认证服务类"""
    
    def register(self, username: str, email: str, password: str) -> Dict:
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
        
        Returns:
            用户信息和token
        """
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            raise ValueError("邮箱已被注册")
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 生成token
        access_token = create_access_token(identity=user.id)
        
        return {
            'user': user.to_dict(),
            'access_token': access_token
        }
    
    def login(self, username: Optional[str] = None, email: Optional[str] = None, password: str = '') -> Dict:
        """
        用户登录
        
        Args:
            username: 用户名（可选）
            email: 邮箱（可选）
            password: 密码
        
        Returns:
            用户信息和token
        """
        if not username and not email:
            raise ValueError("用户名或邮箱不能为空")
        
        # 查找用户
        if username:
            user = User.query.filter_by(username=username).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError("用户名或密码错误")
        
        if not user.check_password(password):
            raise ValueError("用户名或密码错误")
        
        if not user.is_active:
            raise ValueError("账户已被禁用")
        
        # 生成token
        access_token = create_access_token(identity=user.id)
        
        return {
            'user': user.to_dict(),
            'access_token': access_token
        }
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户对象
        """
        return User.query.get(user_id)
    
    def list_users(self) -> list:
        """
        获取所有用户列表
        
        Returns:
            用户列表
        """
        return User.query.order_by(User.created_at.desc()).all()
    
    def update_user_status(self, user_id: int, is_active: bool) -> User:
        """
        更新用户状态
        
        Args:
            user_id: 用户ID
            is_active: 是否激活
        
        Returns:
            更新后的用户对象
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        user.is_active = is_active
        db.session.commit()
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否删除成功
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        db.session.delete(user)
        db.session.commit()
        return True

