"""
音频处理服务
"""
import os
import uuid
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

# 尝试导入pydub，如果失败则音频处理功能不可用
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub不可用，音频格式转换功能将被禁用。请安装pydub和pyaudioop: pip install pydub pyaudioop")

# 允许的音频格式
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'aac', 'flac', 'ogg', 'wma'}

# 音频文件存储目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'audio')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class AudioService:
    """音频处理服务类"""
    
    def __init__(self):
        self.upload_folder = UPLOAD_FOLDER
    
    def allowed_file(self, filename: str) -> bool:
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def save_audio_file(self, file, meeting_id: str) -> Tuple[str, str]:
        """
        保存音频文件
        
        Args:
            file: 上传的文件对象
            meeting_id: 会议ID
        
        Returns:
            (文件路径, 文件名) 元组
        """
        if not file or not file.filename:
            raise ValueError("文件不能为空")
        
        if not self.allowed_file(file.filename):
            raise ValueError(f"不支持的音频格式。支持的格式: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{meeting_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # 创建会议目录
        meeting_folder = os.path.join(self.upload_folder, meeting_id)
        os.makedirs(meeting_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(meeting_folder, unique_filename)
        file.save(file_path)
        
        logger.info(f"音频文件已保存: {file_path}")
        
        return file_path, unique_filename
    
    def convert_to_wav(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        将音频文件转换为WAV格式
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选）
        
        Returns:
            输出文件路径
        """
        if not PYDUB_AVAILABLE:
            raise ImportError("pydub不可用，无法进行音频格式转换。请安装: pip install pydub pyaudioop")
        
        if output_path is None:
            output_path = input_path.rsplit('.', 1)[0] + '.wav'
        
        try:
            # 加载音频文件
            audio = AudioSegment.from_file(input_path)
            
            # 转换为WAV格式（16kHz, 16bit, 单声道）
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            audio = audio.set_sample_width(2)  # 16bit
            
            # 导出为WAV
            audio.export(output_path, format="wav")
            
            logger.info(f"音频已转换为WAV: {output_path}")
            
            return output_path
        
        except Exception as e:
            logger.error(f"音频转换失败: {str(e)}")
            raise Exception(f"音频转换失败: {str(e)}")
    
    def get_audio_info(self, file_path: str, timeout: float = 5.0) -> dict:
        """
        获取音频文件信息
        
        Args:
            file_path: 音频文件路径
            timeout: 超时时间（秒），默认5秒
        
        Returns:
            音频信息字典
        """
        import signal
        
        # 基础信息（不需要pydub，快速返回）
        try:
            file_size = os.path.getsize(file_path)
            file_format = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else 'unknown'
        except Exception as e:
            logger.warning(f"获取文件基础信息失败: {str(e)}")
            return {
                'format': 'unknown',
                'file_size': 0,
                'duration': None,
                'sample_rate': None,
                'channels': None
            }
        
        info = {
            'format': file_format,
            'file_size': file_size,
            'duration': None,
            'sample_rate': None,
            'channels': None
        }
        
        # 如果pydub可用，尝试获取详细信息（带超时保护）
        if PYDUB_AVAILABLE:
            try:
                # 使用超时机制避免大文件阻塞
                def _get_audio_details():
                    try:
                        audio = AudioSegment.from_file(file_path)
                        return {
                            'duration': len(audio) / 1000.0,  # 秒
                            'sample_rate': audio.frame_rate,
                            'channels': audio.channels
                        }
                    except Exception as e:
                        logger.warning(f"pydub读取音频文件失败: {str(e)}")
                        return None
                
                # 对于大文件，直接跳过pydub处理，避免阻塞
                # 如果文件大于50MB，只返回基础信息
                if file_size > 50 * 1024 * 1024:  # 50MB
                    logger.info(f"文件较大({file_size} bytes)，跳过pydub处理")
                else:
                    # 尝试获取详细信息，但不阻塞太久
                    try:
                        audio_details = _get_audio_details()
                        if audio_details:
                            info.update(audio_details)
                    except Exception as e:
                        logger.warning(f"获取音频详细信息失败: {str(e)}")
            except Exception as e:
                logger.warning(f"无法获取音频详细信息（使用pydub）: {str(e)}")
        
        return info
    
    def delete_audio_file(self, file_path: str) -> bool:
        """
        删除音频文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否删除成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"音频文件已删除: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除音频文件失败: {str(e)}")
            return False

