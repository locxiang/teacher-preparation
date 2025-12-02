"""
通义听悟API路由（用于Demo测试）
"""
import logging
import traceback
from flask import Blueprint, request, jsonify
from services.tytingwu_service import TyingWuService

logger = logging.getLogger(__name__)
tytingwu_bp = Blueprint('tytingwu', __name__)
tytingwu_service = TyingWuService()


@tytingwu_bp.route('/create-task', methods=['POST'])
def create_realtime_task():
    """
    创建实时转写任务（用于Demo测试）
    
    根据阿里云文档：https://help.aliyun.com/zh/tingwu/interface-and-implementation
    """
    try:
        data = request.get_json() or {}
        logger.info('=== 创建实时转写任务请求 ===')
        logger.info(f'请求参数: {data}')
        
        # 获取参数
        audio_format = data.get('audio_format', 'pcm')
        sample_rate = data.get('sample_rate', 16000)
        source_language = data.get('source_language', 'cn')
        language_hints = data.get('language_hints')
        task_key = data.get('task_key')
        enable_progressive_callbacks = data.get('enable_progressive_callbacks', False)
        enable_translation = data.get('enable_translation', False)
        translation_target_languages = data.get('translation_target_languages')
        enable_summary = data.get('enable_summary', False)
        summary_types = data.get('summary_types')  # 摘要类型列表：['Paragraph', 'Conversational', 'QuestionsAnswering', 'MindMap']
        enable_key_points = data.get('enable_key_points', False)
        meeting_assistance_types = data.get('meeting_assistance_types')  # 要点提炼类型列表：['Actions', 'KeyInformation']
        enable_diarization = data.get('enable_diarization', True)  # 说话人分离，默认开启
        speaker_count = data.get('speaker_count')  # 说话人数，None表示不定人数
        enable_text_polish = data.get('enable_text_polish', True)  # 口语书面化，默认开启
        
        logger.info(f'解析后的参数: audio_format={audio_format}, sample_rate={sample_rate}, source_language={source_language}')
        logger.info(f'其他参数: task_key={task_key}, enable_summary={enable_summary}, summary_types={summary_types}, enable_key_points={enable_key_points}, meeting_assistance_types={meeting_assistance_types}')
        logger.info(f'说话人分离参数: enable_diarization={enable_diarization}, speaker_count={speaker_count}')
        
        # 检查配置
        logger.info(f'通义听悟配置状态: is_configured={tytingwu_service.is_configured}')
        if not tytingwu_service.is_configured:
            logger.warning('通义听悟未配置，将返回模拟数据')
        
        # 创建实时转写任务
        logger.info('开始调用 create_realtime_task...')
        result = tytingwu_service.create_realtime_task(
            audio_format=audio_format,
            sample_rate=sample_rate,
            source_language=source_language,
            language_hints=language_hints,
            task_key=task_key,
            enable_progressive_callbacks=enable_progressive_callbacks,
            enable_translation=enable_translation,
            translation_target_languages=translation_target_languages,
            enable_summary=enable_summary,
            summary_types=summary_types,
            enable_key_points=enable_key_points,
            meeting_assistance_types=meeting_assistance_types,
            enable_diarization=enable_diarization,
            speaker_count=speaker_count,
            enable_text_polish=enable_text_polish
        )
        
        logger.info(f'创建任务成功，返回结果: TaskId={result.get("TaskId")}, MeetingJoinUrl存在={bool(result.get("MeetingJoinUrl"))}')
        logger.info('=== 创建实时转写任务完成 ===')
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except Exception as e:
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        logger.error('=== 创建实时转写任务失败 ===')
        logger.error(f'错误信息: {error_msg}')
        logger.error(f'错误堆栈:\n{error_traceback}')
        logger.error('=== 错误详情结束 ===')
        
        return jsonify({
            'success': False,
            'message': error_msg,
            'error_type': type(e).__name__
        }), 500


@tytingwu_bp.route('/stop-task', methods=['POST'])
def stop_task():
    """
    停止实时转写任务
    """
    try:
        data = request.get_json() or {}
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({
                'success': False,
                'message': 'task_id不能为空'
            }), 400
        
        result = tytingwu_service.stop_task(task_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@tytingwu_bp.route('/task-info/<task_id>', methods=['GET'])
def get_task_info(task_id):
    """
    查询任务信息
    """
    try:
        result = tytingwu_service.get_task_info(task_id)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

