"""
AI对话路由 - SSE流式响应
使用阿里云百炼 DashScope SDK
"""
from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
import json
import os
import logging

# 导入 DashScope SDK
try:
    from dashscope import Application
    from http import HTTPStatus
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    logging.warning("DashScope SDK 未安装，请运行: pip install dashscope")

ai_chat_bp = Blueprint('ai_chat', __name__)
logger = logging.getLogger(__name__)


@ai_chat_bp.route('/stream', methods=['POST'])
@jwt_required()
def stream_ai_chat():
    """流式AI对话 - 返回SSE流"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        meeting_id = data.get('meeting_id')
        chat_history = data.get('chat_history', '')
        
        # 检查配置
        if not DASHSCOPE_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'DashScope SDK 未安装，请运行: pip install dashscope'
            }), 500
        
        if not Config.DASHSCOPE_API_KEY:
            return jsonify({
                'success': False,
                'message': 'DASHSCOPE_API_KEY 未配置，请在环境变量或 .env 文件中设置'
            }), 500
        
        if not Config.DASHSCOPE_APP_ID:
            return jsonify({
                'success': False,
                'message': 'DASHSCOPE_APP_ID 未配置，请在环境变量或 .env 文件中设置'
            }), 500
        
        # 构建提示词
        prompt = build_prompt(meeting_id, chat_history)
        
        def generate():
            """生成SSE流"""
            try:
                # 尝试流式调用
                try:
                    response = Application.call(
                        api_key=Config.DASHSCOPE_API_KEY,
                        app_id=Config.DASHSCOPE_APP_ID,
                        prompt=prompt,
                        stream=True  # 启用流式响应
                    )
                    
                    # 检查是否是流式响应（可迭代对象）
                    if hasattr(response, '__iter__') and not isinstance(response, (str, bytes)):
                        # 流式响应处理
                        # DashScope SDK 的流式响应返回的是累积的完整文本，需要提取增量
                        accumulated_text = ""
                        for chunk in response:
                            text = None
                            
                            # 尝试多种方式提取文本
                            if hasattr(chunk, 'output') and hasattr(chunk.output, 'text'):
                                text = chunk.output.text
                            elif hasattr(chunk, 'output') and isinstance(chunk.output, dict):
                                text = chunk.output.get('text', '')
                            elif isinstance(chunk, dict):
                                output = chunk.get('output', {})
                                if isinstance(output, dict):
                                    text = output.get('text', '')
                                else:
                                    text = str(output) if output else None
                            
                            if text:
                                # 检查是否是累积文本（DashScope SDK 通常返回累积的完整文本）
                                if text.startswith(accumulated_text):
                                    # 提取增量部分
                                    incremental_text = text[len(accumulated_text):]
                                    accumulated_text = text
                                    
                                    if incremental_text:
                                        chunk_data = {
                                            "content": incremental_text
                                        }
                                        yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                                else:
                                    # 如果不是累积文本，直接发送（可能是增量格式）
                                    accumulated_text = text
                                    chunk_data = {
                                        "content": text
                                    }
                                    yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                    
                    # 非流式响应（单个响应对象）
                    elif response.status_code == HTTPStatus.OK:
                        text = None
                        if hasattr(response, 'output') and hasattr(response.output, 'text'):
                            text = response.output.text
                        elif hasattr(response, 'output') and isinstance(response.output, dict):
                            text = response.output.get('text', '')
                        
                        if text:
                            # 逐词发送以模拟流式效果
                            import re
                            words = re.findall(r'\S+|\s+', text)
                            for word in words:
                                chunk_data = {
                                    "content": word
                                }
                                yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                        else:
                            # 如果无法提取文本，尝试直接使用响应对象
                            response_text = str(response.output) if hasattr(response, 'output') else str(response)
                            import re
                            words = re.findall(r'\S+|\s+', response_text)
                            for word in words:
                                chunk_data = {
                                    "content": word
                                }
                                yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                    else:
                        # 流式调用失败，尝试非流式调用
                        raise Exception(f"流式调用返回错误状态码: {response.status_code}")
                        
                except Exception as stream_error:
                    # 如果流式调用失败，回退到非流式调用
                    logger.warning(f"流式调用失败: {str(stream_error)}，尝试非流式调用")
                    
                    response = Application.call(
                        api_key=Config.DASHSCOPE_API_KEY,
                        app_id=Config.DASHSCOPE_APP_ID,
                        prompt=prompt
                    )
                    
                    if response.status_code == HTTPStatus.OK:
                        text = None
                        if hasattr(response, 'output') and hasattr(response.output, 'text'):
                            text = response.output.text
                        elif hasattr(response, 'output') and isinstance(response.output, dict):
                            text = response.output.get('text', '')
                        else:
                            text = str(response.output) if hasattr(response, 'output') else str(response)
                        
                        if text:
                            # 逐词发送以模拟流式效果
                            import re
                            words = re.findall(r'\S+|\s+', text)
                            for word in words:
                                chunk_data = {
                                    "content": word
                                }
                                yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                    else:
                        error_msg = f"API调用失败: {response.message if hasattr(response, 'message') else '未知错误'} (状态码: {response.status_code})"
                        logger.error(error_msg)
                        error_data = {
                            "error": error_msg
                        }
                        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"生成AI回答时出错: {str(e)}", exc_info=True)
                error_data = {
                    "error": f"AI对话失败: {str(e)}"
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',  # 禁用Nginx缓冲
            }
        )
        
    except Exception as e:
        logger.error(f"AI对话路由错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'AI对话失败: {str(e)}'
        }), 500


def build_prompt(meeting_id: str, chat_history: str) -> str:
    """构建提示词"""
    prompt_parts = []
    
    if meeting_id:
        prompt_parts.append(f"会议ID: {meeting_id}")
    
    if chat_history:
        prompt_parts.append(f"聊天记录:\n{chat_history}")
    
    if not prompt_parts:
        return "请为我总结一下会议内容。"
    
    prompt = "\n\n".join(prompt_parts)
    prompt += "\n\n请根据以上信息，为我提供智能分析和建议。"
    
    return prompt

