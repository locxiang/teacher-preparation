"""
路由模块
"""
from routes.health import health_bp
from routes.meeting import meeting_bp
from routes.auth import auth_bp
from routes.summary import summary_bp
from routes.ai_chat import ai_chat_bp
from routes.tts import tts_bp

__all__ = ['health_bp', 'meeting_bp', 'auth_bp', 'summary_bp', 'ai_chat_bp', 'tts_bp']

