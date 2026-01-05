"""
会议路由
"""
from flask import Blueprint, request, jsonify, Response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.meeting_service import MeetingService
from services.tytingwu_service import TyingWuService
import logging
import json
import time
from datetime import datetime

meeting_bp = Blueprint('meeting', __name__)
meeting_service = MeetingService()
tytingwu_service = TyingWuService()
logger = logging.getLogger(__name__)


@meeting_bp.route('', methods=['POST'])
@jwt_required()
def create_meeting():
    """创建会议"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        meeting_name = data.get('name')
        
        if not meeting_name:
            return jsonify({
                'success': False,
                'message': '会议名称不能为空'
            }), 400
        
        teacher_ids = data.get('teacher_ids', [])  # 获取选择的教师ID列表
        host_teacher_id = data.get('host_teacher_id')  # 获取主持人教师ID
        subject = data.get('subject')  # 获取学科
        grade = data.get('grade')  # 获取年级
        lesson_type = data.get('lesson_type')  # 获取备课类型
        
        meeting = meeting_service.create_meeting(
            meeting_name=meeting_name,
            user_id=user_id,
            description=data.get('description'),
            subject=subject,
            grade=grade,
            lesson_type=lesson_type,
            teacher_ids=teacher_ids,
            host_teacher_id=host_teacher_id
        )
        
        return jsonify({
            'success': True,
            'data': meeting
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('/<meeting_id>', methods=['GET'])
@jwt_required()
def get_meeting(meeting_id):
    """获取会议信息"""
    try:
        user_id = get_jwt_identity()
        meeting = meeting_service.get_meeting(meeting_id, user_id=user_id)
        
        if not meeting:
            return jsonify({
                'success': False,
                'message': '会议不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': meeting
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('', methods=['GET'])
@jwt_required()
def list_meetings():
    """列出所有会议"""
    try:
        user_id = get_jwt_identity()
        status = request.args.get('status')
        meetings = meeting_service.list_meetings(user_id=user_id, status=status)
        
        return jsonify({
            'success': True,
            'data': meetings,
            'total': len(meetings)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('/<meeting_id>/stop', methods=['POST'])
@jwt_required()
def stop_meeting(meeting_id):
    """停止会议"""
    try:
        user_id = get_jwt_identity()
        meeting = meeting_service.stop_meeting(meeting_id, user_id=user_id)
        
        return jsonify({
            'success': True,
            'data': meeting,
            'message': '会议已停止'
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('/<meeting_id>/complete', methods=['POST'])
@jwt_required()
def complete_meeting(meeting_id):
    """完成会议"""
    try:
        user_id = get_jwt_identity()
        meeting = meeting_service.complete_meeting(meeting_id, user_id=user_id)
        
        return jsonify({
            'success': True,
            'data': meeting,
            'message': '会议已标记为已完成'
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('/<meeting_id>/transcript', methods=['PUT', 'POST'])
@jwt_required()
def update_transcript(meeting_id):
    """
    追加单条消息到转写记录（推荐使用）
    或更新整个转写文本（兼容旧接口）
    
    PUT /api/meetings/{meeting_id}/transcript
    Body: {
        "transcript": "完整文本..."  // 旧格式，兼容
    }
    
    POST /api/meetings/{meeting_id}/transcript
    Body: {
        "name": "说话人",
        "time": 1234567890,  // Unix时间戳（毫秒）
        "type": "human" | "ai",
        "content": "消息内容"
    }
    """
    try:
        data = request.get_json() or {}
        
        # 检查是新格式（单条消息）还是旧格式（完整文本）
        if 'name' in data and 'time' in data and 'type' in data and 'content' in data:
            # 新格式：追加单条消息
            message = {
                'name': data.get('name'),
                'time': data.get('time'),
                'type': data.get('type'),
                'content': data.get('content')
            }
            meeting = meeting_service.append_message(meeting_id, message)
            
            return jsonify({
                'success': True,
                'data': meeting,
                'message': '消息已追加'
            }), 200
        else:
            # 旧格式：更新整个转写文本（兼容）
            transcript = data.get('transcript', '')
            meeting = meeting_service.update_transcript(meeting_id, transcript)
            
            return jsonify({
                'success': True,
                'data': meeting,
                'message': '转写文本已更新'
            }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('/<meeting_id>/summary/stream', methods=['GET'])
@jwt_required()
def generate_summary_stream(meeting_id):
    """生成会议摘要 - SSE流式接口"""
    try:
        user_id = get_jwt_identity()
        
        # 验证会议权限
        meeting = meeting_service.get_meeting(meeting_id)
        if not meeting:
            return jsonify({
                'success': False,
                'message': '会议不存在'
            }), 404
        
        if meeting.get('user_id') != user_id:
            return jsonify({
                'success': False,
                'message': '无权访问此会议'
            }), 403
        
        if not meeting.get('task_id'):
            return jsonify({
                'success': False,
                'message': '会议没有关联的通义听悟任务'
            }), 400
        
        def generate():
            """生成SSE流"""
            # 在生成器函数内部导入 app，避免循环导入
            from app import app
            
            try:
                task_id = meeting['task_id']
                max_polls = 300  # 最多轮询5分钟（300秒）
                poll_count = 0
                
                # 发送开始消息
                yield f"data: {json.dumps({'type': 'start', 'message': '开始查询任务状态...'}, ensure_ascii=False)}\n\n"
                
                while poll_count < max_polls:
                    # 查询任务信息
                    yield f"data: {json.dumps({'type': 'status', 'message': f'正在查询任务状态... (第 {poll_count + 1} 次)'}, ensure_ascii=False)}\n\n"
                    
                    task_info = tytingwu_service.get_task_info(task_id)
                    
                    if task_info.get('Code') != '0':
                        error_msg = task_info.get('Message', '查询任务信息失败')
                        yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"
                        break
                    
                    task_data = task_info.get('Data', {})
                    task_status = task_data.get('TaskStatus', 'UNKNOWN')
                    
                    yield f"data: {json.dumps({'type': 'status', 'message': f'任务状态: {task_status}'}, ensure_ascii=False)}\n\n"
                    
                    # 如果任务还在进行中，继续轮询
                    if task_status == 'ONGOING':
                        poll_count += 1
                        time.sleep(1)  # 等待1秒
                        continue
                    
                    # 如果任务被暂停，尝试继续等待（可能自动恢复）
                    if task_status == 'PAUSED':
                        yield f"data: {json.dumps({'type': 'status', 'message': '任务已暂停，等待恢复中...'}, ensure_ascii=False)}\n\n"
                        # 对于暂停状态，可以等待一段时间看是否恢复
                        # 最多等待20次（20秒）
                        pause_wait_count = 0
                        max_pause_waits = 20
                        while pause_wait_count < max_pause_waits:
                            time.sleep(1)
                            pause_wait_count += 1
                            poll_count += 1
                            
                            # 重新查询任务状态
                            task_info = tytingwu_service.get_task_info(task_id)
                            if task_info.get('Code') == '0':
                                task_data = task_info.get('Data', {})
                                task_status = task_data.get('TaskStatus', 'UNKNOWN')
                                yield f"data: {json.dumps({'type': 'status', 'message': f'任务状态: {task_status} (等待恢复中，已等待 {pause_wait_count} 秒)'}, ensure_ascii=False)}\n\n"
                                
                                # 如果状态恢复为 ONGOING 或 COMPLETED，跳出等待循环
                                if task_status in ['ONGOING', 'COMPLETED']:
                                    break
                                elif task_status != 'PAUSED':
                                    # 状态变为其他状态（如 FAILED），跳出等待循环
                                    break
                        
                        # 如果等待后仍然是 PAUSED，提示错误
                        if task_status == 'PAUSED':
                            yield f"data: {json.dumps({'type': 'error', 'message': '任务出现异常，无法总结'}, ensure_ascii=False)}\n\n"
                            break
                        
                        # 如果状态变为 ONGOING，继续轮询
                        if task_status == 'ONGOING':
                            continue
                        # 如果状态变为 COMPLETED，继续处理（会进入下面的 COMPLETED 分支）
                    
                    # 任务已完成或失败，开始处理结果
                    if task_status == 'COMPLETED':
                        yield f"data: {json.dumps({'type': 'status', 'message': '任务已完成，开始下载结果...'}, ensure_ascii=False)}\n\n"
                        
                        # 处理结果URL
                        result_urls = task_data.get('Result', {})
                        
                        # 下载并处理 Summarization
                        if result_urls.get('Summarization'):
                            yield f"data: {json.dumps({'type': 'status', 'message': '正在下载摘要结果...'}, ensure_ascii=False)}\n\n"
                            try:
                                downloaded_data = tytingwu_service._download_json_from_url(result_urls['Summarization'])
                                if isinstance(downloaded_data, dict) and 'Summarization' in downloaded_data:
                                    task_data['Summarization'] = downloaded_data['Summarization']
                                    yield f"data: {json.dumps({'type': 'status', 'message': '摘要结果下载完成'}, ensure_ascii=False)}\n\n"
                            except Exception as e:
                                yield f"data: {json.dumps({'type': 'warning', 'message': f'下载摘要结果失败: {str(e)}'}, ensure_ascii=False)}\n\n"
                        
                        # 下载并处理 MeetingAssistance
                        if result_urls.get('MeetingAssistance'):
                            yield f"data: {json.dumps({'type': 'status', 'message': '正在下载要点提炼结果...'}, ensure_ascii=False)}\n\n"
                            try:
                                downloaded_data = tytingwu_service._download_json_from_url(result_urls['MeetingAssistance'])
                                if isinstance(downloaded_data, dict) and 'MeetingAssistance' in downloaded_data:
                                    task_data['MeetingAssistance'] = downloaded_data['MeetingAssistance']
                                    yield f"data: {json.dumps({'type': 'status', 'message': '要点提炼结果下载完成'}, ensure_ascii=False)}\n\n"
                            except Exception as e:
                                yield f"data: {json.dumps({'type': 'warning', 'message': f'下载要点提炼结果失败: {str(e)}'}, ensure_ascii=False)}\n\n"
                        
                        # 保存 MP3 音频 URL（不需要下载，直接使用 OutputMp3Path）
                        if result_urls.get('OutputMp3Path') or task_data.get('OutputMp3Path'):
                            mp3_url = result_urls.get('OutputMp3Path') or task_data.get('OutputMp3Path')
                            # 将 MP3 URL 保存到 task_data 中，后续会保存到数据库
                            task_data['mp3_url'] = mp3_url
                            yield f"data: {json.dumps({'type': 'status', 'message': '音频文件URL已获取', 'mp3_url': mp3_url}, ensure_ascii=False)}\n\n"
                        
                        # 保存摘要结果到数据库
                        yield f"data: {json.dumps({'type': 'status', 'message': '正在保存摘要结果...'}, ensure_ascii=False)}\n\n"
                        # 使用应用上下文包裹数据库操作
                        with app.app_context():
                            meeting_result = meeting_service.save_summary_from_task_data(meeting_id, task_data)
                        
                        yield f"data: {json.dumps({'type': 'complete', 'data': meeting_result, 'message': '摘要生成完成'}, ensure_ascii=False)}\n\n"
                        break
                    
                    elif task_status in ['FAILED', 'INVALID']:
                        error_msg = task_data.get('ErrorMessage', f'任务状态: {task_status}')
                        yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"
                        break
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'message': f'未知任务状态: {task_status}'}, ensure_ascii=False)}\n\n"
                        break
                
                if poll_count >= max_polls:
                    yield f"data: {json.dumps({'type': 'error', 'message': '查询超时，请稍后重试'}, ensure_ascii=False)}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"生成摘要流时出错: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': f'处理失败: {str(e)}'}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
            }
        )
    
    except Exception as e:
        logger.error(f"摘要生成流式接口错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('/<meeting_id>/task', methods=['PUT'])
@jwt_required()
def update_meeting_task(meeting_id):
    """更新会议的任务信息"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        task_id = data.get('task_id')
        stream_url = data.get('stream_url')
        
        if not task_id or not stream_url:
            return jsonify({
                'success': False,
                'message': 'task_id和stream_url不能为空'
            }), 400
        
        meeting = meeting_service.update_meeting_task(meeting_id, task_id, stream_url, user_id=user_id)
        
        return jsonify({
            'success': True,
            'data': meeting,
            'message': '会议任务信息已更新'
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('/<meeting_id>', methods=['DELETE'])
@jwt_required()
def delete_meeting(meeting_id):
    """删除会议"""
    try:
        user_id = get_jwt_identity()
        meeting_service.delete_meeting(meeting_id, user_id=user_id)
        
        return jsonify({
            'success': True,
            'message': '会议已删除'
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@meeting_bp.route('/<meeting_id>/summary/download', methods=['GET'])
@jwt_required()
def download_summary(meeting_id):
    """下载会议总结Word文档"""
    try:
        user_id = get_jwt_identity()
        
        # 验证会议权限
        meeting = meeting_service.get_meeting(meeting_id, user_id=user_id)
        if not meeting:
            return jsonify({
                'success': False,
                'message': '会议不存在或无权限'
            }), 404
        
        # 生成Word文档
        doc_bytes = meeting_service.generate_summary_document(meeting_id, user_id=user_id)
        
        # 生成文件名
        meeting_name = meeting.get('name', '会议总结')
        # 清理文件名中的特殊字符
        safe_name = ''.join(c for c in meeting_name if c.isalnum() or c in (' ', '-', '_'))[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.docx"
        
        return send_file(
            doc_bytes,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
    
    except ValueError as e:
        logger.error(f"下载会议总结失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"下载会议总结失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

