"""
阿里云通义听悟实时转写SDK服务
使用官方SDK实现实时音频流推送和转写结果接收
"""
import logging
import traceback
from typing import Dict, Optional, Callable
from config import Config

logger = logging.getLogger(__name__)

# 尝试导入官方SDK
try:
    # 阿里云智能语音交互实时转写SDK
    # 安装方式: 下载whl文件后执行: pip install nls-1.1.0-py3-none-any.whl
    # 下载地址: https://help.aliyun.com/zh/tingwu/install-the-sdk
    from nls import SpeechTranscriber
    SDK_AVAILABLE = True
    logger.info('✓ 阿里云实时转写SDK已导入')
except ImportError as e:
    SDK_AVAILABLE = False
    logger.warning(f'阿里云实时转写SDK未安装: {str(e)}')
    logger.warning('请安装SDK: 下载whl文件后执行 pip install nls-1.1.0-py3-none-any.whl')
    logger.warning('下载地址: https://help.aliyun.com/zh/tingwu/install-the-sdk')
    # 定义占位类，避免导入错误
    class SpeechTranscriber:
        pass


class TyingWuRealtimeSDK:
    """使用官方SDK的实时转写服务"""
    
    def __init__(self):
        self.access_key_id = Config.ALIBABA_CLOUD_ACCESS_KEY_ID
        self.access_key_secret = Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET
        self.app_key = Config.TYTINGWU_APP_KEY
        
        self.is_configured = bool(
            self.access_key_id and 
            self.access_key_secret and 
            self.app_key and
            SDK_AVAILABLE
        )
        
        if not SDK_AVAILABLE:
            logger.error('阿里云实时转写SDK未安装，无法使用实时转写功能')
        elif not self.is_configured:
            logger.warning('通义听悟配置不完整')
    
    def create_transcriber(
        self,
        on_result: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        audio_format: str = 'pcm',
        sample_rate: int = 16000,
        language: str = 'zh'
    ) -> Optional[SpeechTranscriber]:
        """
        创建实时转写器实例
        
        Args:
            on_result: 转写结果回调函数
            on_error: 错误回调函数
            audio_format: 音频格式
            sample_rate: 采样率
            language: 语言代码
        
        Returns:
            SpeechTranscriber实例或None
        """
        if not self.is_configured:
            logger.error('配置不完整，无法创建转写器')
            return None
        
        if not SDK_AVAILABLE:
            logger.error('SDK未安装，无法创建转写器')
            return None
        
        try:
            logger.info('=== 创建实时转写器 ===')
            logger.info(f'参数: audio_format={audio_format}, sample_rate={sample_rate}, language={language}')
            
            # 创建转写器实例
            transcriber = SpeechTranscriber(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                app_key=self.app_key,
                on_result=on_result or self._default_on_result,
                on_error=on_error or self._default_on_error,
                format=audio_format,
                sample_rate=sample_rate,
                language=language
            )
            
            logger.info('✓ 实时转写器创建成功')
            return transcriber
            
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error('=== 创建实时转写器失败 ===')
            logger.error(f'错误类型: {type(e).__name__}')
            logger.error(f'错误信息: {str(e)}')
            logger.error(f'错误堆栈:\n{error_traceback}')
            return None
    
    def _default_on_result(self, message: Dict):
        """默认结果回调"""
        logger.info(f'收到转写结果: {message}')
    
    def _default_on_error(self, message: Dict):
        """默认错误回调"""
        logger.error(f'转写错误: {message}')

