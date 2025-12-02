"""
WebSocket服务 - 用于实时转写
"""
import json
import logging
import base64
import time
from typing import Dict, Optional
from flask_socketio import SocketIO, emit, join_room, leave_room
from services.meeting_service import MeetingService
from services.tytingwu_websocket import WebSocketManager, TyingWuWebSocketClient

logger = logging.getLogger(__name__)

# 全局SocketIO实例（将在app.py中初始化）
socketio = None
meeting_service = MeetingService()
# 通义听悟WebSocket连接管理器
ws_manager = WebSocketManager()


def init_socketio(app):
    """初始化SocketIO并注册事件处理器"""
    global socketio
    # 使用threading模式，避免async_mode问题
    # 参考：https://flask-socketio.readthedocs.io/en/latest/deployment.html
    try:
        socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=False,  # 禁用SocketIO的默认日志，使用我们的logger
            engineio_logger=False,
            ping_timeout=60,
            ping_interval=25
        )
    except Exception as e:
        # 如果threading模式失败，使用默认模式
        import logging
        logging.warning(f"使用threading模式失败，使用默认模式: {str(e)}")
        socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            logger=False,
            engineio_logger=False
        )
    
    # 注册事件处理器
    register_handlers(socketio)
    
    return socketio


def register_handlers(sio):
    """注册WebSocket事件处理器"""
    
    @sio.on('connect')
    def handle_connect(auth):
        """客户端连接"""
        try:
            logger.info('客户端已连接')
            emit('connected', {'message': '连接成功'})
        except Exception as e:
            logger.error(f'处理连接事件失败: {str(e)}')
    
    @sio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接"""
        try:
            logger.info('客户端已断开连接')
        except Exception as e:
            logger.error(f'处理断开连接事件失败: {str(e)}')
    
    @sio.on('join_meeting')
    def handle_join_meeting(data):
        """加入会议房间"""
        try:
            meeting_id = data.get('meeting_id')
            if not meeting_id:
                emit('error', {'message': '会议ID不能为空'})
                return
            
            # Demo场景：允许mock TaskId跳过数据库检查
            meeting = meeting_service.get_meeting(meeting_id)
            if not meeting:
                # 检查是否是Demo场景（mock TaskId）
                if meeting_id.startswith('mock_task_') or 'mock' in meeting_id.lower():
                    logger.info(f'Demo模式：允许mock TaskId加入房间，meeting_id={meeting_id}')
                    # 允许加入房间，但不检查数据库
                    join_room(meeting_id)
                    emit('joined', {
                        'meeting_id': meeting_id,
                        'message': '已加入会议房间（Demo模式）'
                    })
                    logger.info(f'客户端加入会议房间（Demo模式）: {meeting_id}')
                    return
                else:
                    emit('error', {'message': '会议不存在'})
                    return
            
            # 加入房间
            join_room(meeting_id)
            
            emit('joined', {
                'meeting_id': meeting_id,
                'message': '已加入会议房间'
            })
            
            logger.info(f'客户端加入会议房间: {meeting_id}')
        
        except Exception as e:
            logger.error(f'加入会议房间失败: {str(e)}')
            emit('error', {'message': str(e)})
    
    @sio.on('leave_meeting')
    def handle_leave_meeting(data):
        """离开会议房间"""
        try:
            meeting_id = data.get('meeting_id')
            if not meeting_id:
                return
            
            # 关闭通义听悟连接（如果存在）
            ws_manager.close_connection(meeting_id)
            
            leave_room(meeting_id)
            
            emit('left', {
                'meeting_id': meeting_id,
                'message': '已离开会议房间'
            })
            
            logger.info(f'客户端离开会议房间: {meeting_id}')
        
        except Exception as e:
            logger.error(f'离开会议房间失败: {str(e)}')
    
    @sio.on('start_recognition')
    def handle_start_recognition(data):
        """开始语音识别，建立通义听悟连接"""
        try:
            meeting_id = data.get('meeting_id')
            if not meeting_id:
                emit('error', {'message': '会议ID不能为空'})
                return
            
            # 尝试从数据库获取会议信息
            meeting = meeting_service.get_meeting(meeting_id)
            
            # 如果会议不存在，检查是否是Demo场景（提供了stream_url）
            stream_url = None
            if meeting:
                stream_url = meeting.get('stream_url')
            else:
                # Demo场景：允许通过data直接提供stream_url
                stream_url = data.get('stream_url')
                if stream_url:
                    logger.info(f'Demo模式：使用提供的stream_url，meeting_id={meeting_id}')
                else:
                    # 检查是否是mock TaskId（Demo测试场景）
                    if meeting_id.startswith('mock_task_') or 'mock' in meeting_id.lower():
                        logger.warning(f'Demo模式：会议不存在但允许继续，meeting_id={meeting_id}')
                        # 对于mock场景，允许继续但不建立真实连接
                        emit('error', {'message': '通义听悟配置不完整，无法创建真实的WebSocket连接。请检查环境变量配置。'})
                        return
                    else:
                        emit('error', {'message': '会议不存在'})
                        return
            
            if not stream_url:
                error_msg = '会议未配置通义听悟流地址。请确保通义听悟配置正确（ALIBABA_CLOUD_ACCESS_KEY_ID、ALIBABA_CLOUD_ACCESS_KEY_SECRET、TYTINGWU_APP_KEY）'
                logger.error(error_msg)
                emit('error', {'message': error_msg})
                return
            
            # 检查是否是mock URL
            if stream_url.startswith('wss://mock-') or 'mock' in stream_url.lower():
                error_msg = '通义听悟配置不完整，无法创建真实的WebSocket连接。请检查环境变量配置。'
                logger.error(error_msg)
                emit('error', {'message': error_msg})
                return
            
            # 定义消息回调函数
            def on_tytingwu_message(message_data):
                """处理通义听悟返回的消息"""
                try:
                    # 解析通义听悟返回的消息
                    # 根据通义听悟文档，消息格式可能包含：
                    # - Sentence: 句子级别的转写结果
                    # - Word: 词级别的转写结果
                    # - Event: 事件消息
                    
                    logger.debug(f'收到通义听悟消息: {message_data}')
                    
                    # 提取转写文本
                    text = None
                    is_final = False
                    timestamp = None
                    
                    # 根据通义听悟文档解析消息格式
                    # 参考：https://help.aliyun.com/zh/tingwu/js-push-stream
                    text = None
                    is_final = False
                    timestamp = None
                    
                    if isinstance(message_data, dict):
                        # 检查消息格式：header + payload
                        header = message_data.get('header', {})
                        payload = message_data.get('payload', {})
                        event_name = header.get('name', '')
                        
                        # 检查是否有错误
                        if 'ErrorCode' in message_data or 'error' in message_data:
                            error_code = message_data.get('ErrorCode') or message_data.get('error', {}).get('code')
                            error_msg = message_data.get('ErrorMessage') or message_data.get('error', {}).get('message', '')
                            logger.error(f'通义听悟返回错误: Code={error_code}, Message={error_msg}')
                            return
                        
                        # 根据事件类型处理
                        # SentenceBegin: 句子开始
                        if event_name == 'SentenceBegin':
                            logger.debug(f'句子开始: {payload.get("index", "unknown")}')
                            return
                        
                        # TranscriptionResultChanged: 句中识别结果变化（中间结果）
                        elif event_name == 'TranscriptionResultChanged':
                            text = payload.get('result', '')
                            is_final = False
                            timestamp = payload.get('time', 0) or int(time.time() * 1000)
                            logger.debug(f'中间结果: {text}')
                        
                        # SentenceEnd: 句子结束（最终结果）
                        elif event_name == 'SentenceEnd':
                            # 最终结果，只使用 result，不使用 stash_result
                            result_text = payload.get('result', '')
                            text = result_text.strip()
                            is_final = True
                            timestamp = payload.get('time', 0) or int(time.time() * 1000)
                            logger.info(f'句子结束（最终结果）: {text}')
                        
                        # ResultTranslated: 翻译结果
                        elif event_name == 'ResultTranslated':
                            translate_result = payload.get('translate_result', {})
                            logger.debug(f'翻译结果: {translate_result}')
                            return  # 翻译结果暂不处理
                        
                        # 兼容旧格式（如果API返回的是旧格式）
                        elif 'Sentence' in message_data:
                            sentence = message_data['Sentence']
                            text = sentence.get('Text', '')
                            is_final = sentence.get('EndTime', 0) > 0
                            timestamp = sentence.get('BeginTime', 0) or sentence.get('EndTime', 0)
                        
                        elif 'Word' in message_data:
                            word = message_data['Word']
                            text = word.get('Word', '')
                            is_final = False
                            timestamp = word.get('BeginTime', 0)
                        
                        elif 'Text' in message_data:
                            text = message_data.get('Text', '')
                            is_final = message_data.get('IsFinal', False)
                            timestamp = message_data.get('Timestamp', 0)
                    
                    if text:
                        # 更新数据库（Demo场景允许失败）
                        try:
                            meeting_service.update_transcript(meeting_id, text)
                        except Exception as e:
                            # Demo场景下，如果会议不存在，允许跳过数据库更新
                            if not (meeting_id.startswith('mock_task_') or 'mock' in meeting_id.lower()):
                                logger.error(f'更新转写文本失败: {str(e)}')
                            else:
                                logger.debug(f'Demo模式：跳过数据库更新，meeting_id={meeting_id}')
                        
                        # 广播给房间内的所有客户端
                        try:
                            sio.emit('transcript_update', {
                                'meeting_id': meeting_id,
                                'text': text,
                                'is_final': is_final,
                                'timestamp': timestamp or int(time.time() * 1000)
                            }, room=meeting_id)
                        except Exception as e:
                            logger.error(f'广播转写结果失败: {str(e)}')
                
                except Exception as e:
                    logger.error(f'处理通义听悟消息失败: {str(e)}')
            
            # 创建或获取通义听悟WebSocket连接
            tytingwu_client = ws_manager.get_connection(meeting_id)
            if not tytingwu_client:
                tytingwu_client = ws_manager.create_connection(
                    meeting_id,
                    stream_url,
                    on_tytingwu_message
                )
            
            emit('recognition_started', {
                'meeting_id': meeting_id,
                'message': '语音识别已启动'
            })
            
            logger.info(f'已启动语音识别，会议ID: {meeting_id}')
        
        except Exception as e:
            logger.error(f'启动语音识别失败: {str(e)}')
            emit('error', {'message': str(e)})
    
    @sio.on('audio_data')
    def handle_audio_data(data):
        """接收音频数据并转发到通义听悟"""
        try:
            meeting_id = data.get('meeting_id')
            audio_data = data.get('audio_data')  # Base64编码的音频数据
            audio_format = data.get('format', 'pcm')  # pcm, wav等
            
            if not meeting_id or not audio_data:
                logger.warning(f'缺少必要参数: meeting_id={meeting_id}, audio_data存在={bool(audio_data)}')
                return
            
            # 检查会议是否存在（Demo场景允许跳过）
            meeting = meeting_service.get_meeting(meeting_id)
            if not meeting:
                # Demo场景：如果已经有WebSocket连接，允许继续发送音频数据
                tytingwu_client = ws_manager.get_connection(meeting_id)
                if not tytingwu_client:
                    # 只有在没有连接且不是mock场景时才警告
                    if not (meeting_id.startswith('mock_task_') or 'mock' in meeting_id.lower()):
                        logger.warning(f'会议不存在且无WebSocket连接: {meeting_id}')
                    return
                # 如果有连接，继续处理（Demo场景）
            
            # 获取通义听悟WebSocket连接
            tytingwu_client = ws_manager.get_connection(meeting_id)
            if not tytingwu_client:
                # 不发送错误，避免日志过多，只在调试时记录
                logger.debug(f'语音识别未启动，会议ID: {meeting_id}')
                return
            
            try:
                # 解码Base64音频数据
                if isinstance(audio_data, str):
                    audio_bytes = base64.b64decode(audio_data)
                else:
                    audio_bytes = audio_data
                
                # 发送音频数据到通义听悟（send_audio内部会等待连接建立）
                tytingwu_client.send_audio(audio_bytes)
                
                logger.debug(f'已转发音频数据，会议ID: {meeting_id}, 数据长度: {len(audio_bytes)}')
            
            except Exception as e:
                # 只在非连接错误时记录，避免日志过多
                error_msg = str(e)
                if 'WebSocket未连接' not in error_msg and '连接超时' not in error_msg:
                    logger.error(f'发送音频数据到通义听悟失败: {error_msg}')
        
        except Exception as e:
            logger.error(f'处理音频数据失败: {str(e)}')
    
    @sio.on('stop_recognition')
    def handle_stop_recognition(data):
        """停止语音识别"""
        try:
            meeting_id = data.get('meeting_id')
            if not meeting_id:
                return
            
            # 获取通义听悟WebSocket连接
            tytingwu_client = ws_manager.get_connection(meeting_id)
            if tytingwu_client and tytingwu_client.connected:
                try:
                    # 发送StopTranscription指令
                    # 根据文档：https://help.aliyun.com/zh/tingwu/js-push-stream
                    stop_message = {
                        'header': {
                            'name': 'StopTranscription',
                            'namespace': 'SpeechTranscriber'
                        },
                        'payload': {}
                    }
                    tytingwu_client.send_text(stop_message)
                    logger.info(f'已发送StopTranscription指令，会议ID: {meeting_id}')
                    
                    # 等待一小段时间确保消息发送完成
                    import time
                    time.sleep(0.1)
                except Exception as e:
                    logger.warning(f'发送StopTranscription指令失败: {str(e)}')
            
            # 关闭通义听悟WebSocket连接
            ws_manager.close_connection(meeting_id)
            
            emit('recognition_stopped', {
                'meeting_id': meeting_id,
                'message': '语音识别已停止'
            })
            
            logger.info(f'已停止语音识别，会议ID: {meeting_id}')
        
        except Exception as e:
            logger.error(f'停止语音识别失败: {str(e)}')
            emit('error', {'message': str(e)})
    
    @sio.on('transcript_result')
    def handle_transcript_result(data):
        """接收通义听悟的转写结果并广播"""
        try:
            meeting_id = data.get('meeting_id')
            transcript_text = data.get('text')
            
            if not meeting_id or not transcript_text:
                return
            
            # 更新会议转写文本
            meeting = meeting_service.update_transcript(meeting_id, transcript_text)
            
            # 广播给房间内的所有客户端
            sio.emit('transcript_update', {
                'meeting_id': meeting_id,
                'text': transcript_text,
                'timestamp': meeting.get('updated_at')
            }, room=meeting_id)
            
            logger.info(f'转写结果已更新，会议ID: {meeting_id}')
        
        except Exception as e:
            logger.error(f'处理转写结果失败: {str(e)}')

