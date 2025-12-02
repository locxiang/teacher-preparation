"""
通义听悟WebSocket客户端
"""
import json
import logging
import websocket
import threading
from typing import Callable, Optional
from services.tytingwu_service import TyingWuService

logger = logging.getLogger(__name__)


class TyingWuWebSocketClient:
    """通义听悟WebSocket客户端"""
    
    def __init__(self, stream_url: str, on_message: Optional[Callable] = None):
        """
        初始化WebSocket客户端
        
        Args:
            stream_url: 通义听悟推流URL
            on_message: 消息回调函数
        """
        self.stream_url = stream_url
        self.on_message = on_message
        self.ws = None
        self.connected = False
        self.thread = None
        self.connection_event = threading.Event()  # 用于等待连接建立
        self.start_transcription_sent = False  # 标记是否已发送StartTranscription
    
    def connect(self):
        """建立WebSocket连接"""
        # 检查URL是否有效（不是mock URL）
        if not self.stream_url or self.stream_url.startswith('wss://mock-'):
            raise Exception(f"无效的WebSocket URL: {self.stream_url}。请确保通义听悟配置正确。")
        
        try:
            self.ws = websocket.WebSocketApp(
                self.stream_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 在单独线程中运行
            self.thread = threading.Thread(target=self.ws.run_forever)
            self.thread.daemon = True
            self.thread.start()
            
            logger.info(f"WebSocket连接已启动: {self.stream_url}")
        
        except Exception as e:
            logger.error(f"WebSocket连接失败: {str(e)}")
            self.connection_event.set()  # 设置事件，避免无限等待
            raise
    
    def _on_open(self, ws):
        """连接打开回调"""
        self.connected = True
        logger.info("WebSocket连接已建立")
        
        try:
            # 发送StartTranscription开始识别指令
            # 根据官方文档：https://help.aliyun.com/zh/tingwu/js-push-stream
            start_message = {
                'header': {
                    'name': 'StartTranscription',
                    'namespace': 'SpeechTranscriber'
                },
                'payload': {
                    'format': 'pcm'  # 音频格式：pcm、opus、aac、speex、mp3
                }
            }
            ws.send(json.dumps(start_message))
            self.start_transcription_sent = True
            logger.info("已发送StartTranscription指令")
        except Exception as e:
            logger.error(f"发送StartTranscription指令失败: {str(e)}")
        
        # 通知连接已建立
        self.connection_event.set()
    
    def _on_message(self, ws, message):
        """接收消息回调"""
        try:
            # 通义听悟返回的是文本消息（JSON格式）
            # 根据文档：https://help.aliyun.com/zh/tingwu/js-push-stream
            if isinstance(message, bytes):
                # 如果是二进制，尝试解码为UTF-8
                try:
                    message = message.decode('utf-8')
                except:
                    logger.debug(f"收到二进制消息，长度: {len(message)}")
                    return
            
            # 解析JSON消息
            data = json.loads(message)
            logger.debug(f"收到通义听悟消息: {data}")
            
            if self.on_message:
                self.on_message(data)
        
        except json.JSONDecodeError as e:
            # 如果不是JSON格式，记录原始消息
            logger.warning(f"收到非JSON消息: {message[:200] if isinstance(message, str) else type(message)}")
            logger.debug(f"JSON解析错误: {str(e)}")
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {str(e)}")
    
    def _on_error(self, ws, error):
        """错误回调"""
        logger.error(f"WebSocket错误: {str(error)}")
        self.connected = False
        self.connection_event.set()  # 即使出错也设置事件，避免无限等待
    
    def _on_close(self, ws, close_status_code, close_msg):
        """连接关闭回调"""
        logger.info(f"WebSocket连接已关闭，状态码: {close_status_code}, 原因: {close_msg}")
        self.connected = False
        self.start_transcription_sent = False
        self.connection_event.clear()
    
    def send_audio(self, audio_data: bytes):
        """
        发送音频数据
        
        Args:
            audio_data: 音频数据（字节）
        """
        # 等待连接建立（最多等待5秒）
        if not self.connection_event.wait(timeout=5):
            if not self.connected:
                raise Exception("WebSocket连接超时")
        
        if not self.connected or not self.ws:
            raise Exception("WebSocket未连接")
        
        # 确保已发送StartTranscription指令
        if not self.start_transcription_sent:
            logger.warning("StartTranscription指令未发送，尝试发送...")
            try:
                # 根据官方文档格式：https://help.aliyun.com/zh/tingwu/js-push-stream
                start_message = {
                    'header': {
                        'name': 'StartTranscription',
                        'namespace': 'SpeechTranscriber'
                    },
                    'payload': {
                        'format': 'pcm'
                    }
                }
                self.ws.send(json.dumps(start_message))
                self.start_transcription_sent = True
                logger.info("已发送StartTranscription指令")
            except Exception as e:
                logger.error(f"发送StartTranscription指令失败: {str(e)}")
                raise Exception(f"无法发送StartTranscription指令: {str(e)}")
        
        try:
            # 根据通义听悟协议发送音频数据（二进制格式）
            # 参考文档：https://help.aliyun.com/zh/tingwu/interface-and-implementation
            self.ws.send(audio_data, opcode=websocket.ABNF.OPCODE_BINARY)
        
        except Exception as e:
            logger.error(f"发送音频数据失败: {str(e)}")
            raise
    
    def send_text(self, message: dict):
        """
        发送文本消息
        
        Args:
            message: 消息字典
        """
        if not self.connected or not self.ws:
            raise Exception("WebSocket未连接")
        
        try:
            self.ws.send(json.dumps(message))
        except Exception as e:
            logger.error(f"发送文本消息失败: {str(e)}")
            raise
    
    def close(self):
        """关闭连接"""
        self.connected = False
        self.start_transcription_sent = False
        self.connection_event.clear()
        
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                logger.warning(f"关闭WebSocket连接时出错: {str(e)}")
        
        logger.info("WebSocket连接已关闭")


# WebSocket连接管理器
class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.connections = {}  # {meeting_id: TyingWuWebSocketClient}
    
    def create_connection(self, meeting_id: str, stream_url: str, on_message: Callable) -> TyingWuWebSocketClient:
        """
        创建WebSocket连接
        
        Args:
            meeting_id: 会议ID
            stream_url: 推流URL
            on_message: 消息回调
        
        Returns:
            WebSocket客户端实例
        """
        # 关闭旧连接（如果存在）
        if meeting_id in self.connections:
            try:
                self.connections[meeting_id].close()
            except Exception as e:
                logger.warning(f"关闭旧连接失败: {str(e)}")
        
        # 创建新连接
        client = TyingWuWebSocketClient(stream_url, on_message)
        try:
            client.connect()
            # 等待连接建立（最多等待3秒）
            if client.connection_event.wait(timeout=3):
                if client.connected:
                    logger.info(f"通义听悟WebSocket连接已建立，会议ID: {meeting_id}")
                else:
                    logger.warning(f"通义听悟WebSocket连接事件触发但未连接，会议ID: {meeting_id}")
            else:
                logger.warning(f"通义听悟WebSocket连接超时，会议ID: {meeting_id}")
        except Exception as e:
            logger.error(f"创建通义听悟WebSocket连接失败: {str(e)}")
            raise
        
        self.connections[meeting_id] = client
        return client
    
    def get_connection(self, meeting_id: str) -> Optional[TyingWuWebSocketClient]:
        """获取连接"""
        return self.connections.get(meeting_id)
    
    def close_connection(self, meeting_id: str):
        """关闭连接"""
        if meeting_id in self.connections:
            self.connections[meeting_id].close()
            del self.connections[meeting_id]
    
    def close_all(self):
        """关闭所有连接"""
        for meeting_id in list(self.connections.keys()):
            self.close_connection(meeting_id)

