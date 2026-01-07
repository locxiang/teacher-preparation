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


def _extract_text_from_response(response_or_chunk):
    """从 DashScope 响应中提取文本内容"""
    if hasattr(response_or_chunk, 'output'):
        output = response_or_chunk.output
        if hasattr(output, 'text'):
            return output.text
        if isinstance(output, dict):
            return output.get('text', '')
        return str(output) if output else None
    if isinstance(response_or_chunk, dict):
        return response_or_chunk.get('output', {}).get('text', '')
    return None


def _send_sse_chunk(content):
    """发送 SSE 数据块"""
    return f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"


def _stream_text_as_words(text):
    """将文本按词分割并逐个发送（用于非流式响应的模拟流式效果）"""
    import re
    for word in re.findall(r'\S+|\s+', text):
        yield _send_sse_chunk(word)


@ai_chat_bp.route('/stream', methods=['POST'])
@jwt_required()
def stream_ai_chat():
    """流式AI对话 - 返回SSE流"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        meeting_id = data.get('meeting_id')
        
        # 处理消息格式（OpenAI风格）
        messages = data.get('messages', [])
        max_history = data.get('max_history')
        
        # 向后兼容：如果传递了 chat_history 字符串
        chat_history_str = data.get('chat_history', '')
        
        # 如果传递了 messages 数组，使用新格式
        if messages and isinstance(messages, list) and len(messages) > 0:
            # 如果指定了 max_history，截取最近的消息
            if max_history and isinstance(max_history, int) and max_history > 0:
                messages = messages[-max_history:]
            
            # 将消息数组转换为字符串格式（用于构建 prompt）
            chat_history_str = '\n\n'.join([
                f"{'用户' if msg.get('role') == 'user' else 'AI助手'}: {msg.get('content', '')}"
                for msg in messages
                if msg.get('content', '').strip()  # 过滤空内容
            ])
        
        # 记录日志以便调试
        logger.info(f"AI对话请求 - meeting_id: {meeting_id}, messages数量: {len(messages) if isinstance(messages, list) else 0}, max_history: {max_history}, chat_history长度: {len(chat_history_str)}")
        logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False, default=str)}")
        
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
        
        # 构建提示词（build_prompt内部会打印详细日志）
        prompt = build_prompt(meeting_id, chat_history_str)
        logger.info(f"[AI对话] 提示词构建完成，总长度: {len(prompt)} 字符")
        
        def generate():
            """生成SSE流"""
            import time
            try:
                logger.info(f"[DashScope API] 开始调用，prompt长度: {len(prompt)} 字符")
                start_time = time.time()
                
                # 尝试流式调用
                try:
                    response = Application.call(
                        api_key=Config.DASHSCOPE_API_KEY,
                        app_id=Config.DASHSCOPE_APP_ID,
                        prompt=prompt,
                        stream=True
                    )
                    
                    # 处理流式响应
                    if hasattr(response, '__iter__') and not isinstance(response, (str, bytes)):
                        accumulated_text = ""
                        for chunk in response:
                            text = _extract_text_from_response(chunk)
                            if text:
                                # DashScope 返回累积文本，提取增量部分
                                if text.startswith(accumulated_text):
                                    incremental = text[len(accumulated_text):]
                                    accumulated_text = text
                                    if incremental:
                                        yield _send_sse_chunk(incremental)
                                else:
                                    accumulated_text = text
                                    yield _send_sse_chunk(text)
                        
                        elapsed = time.time() - start_time
                        logger.info(f"[DashScope API] 流式响应完成，耗时: {elapsed:.2f}秒")
                    
                    # 非流式响应（单个响应对象）
                    elif hasattr(response, 'status_code'):
                        if response.status_code == HTTPStatus.OK:
                            text = _extract_text_from_response(response)
                            if text:
                                yield from _stream_text_as_words(text)
                        else:
                            error_msg = f"API调用失败: {getattr(response, 'message', '未知错误')} (状态码: {response.status_code})"
                            logger.error(error_msg)
                            yield _send_sse_chunk(error_msg)
                    
                except Exception as stream_error:
                    # 流式调用失败，回退到非流式调用
                    logger.warning(f"流式调用失败，回退到非流式: {stream_error}")
                    response = Application.call(
                        api_key=Config.DASHSCOPE_API_KEY,
                        app_id=Config.DASHSCOPE_APP_ID,
                        prompt=prompt
                    )
                    
                    if response.status_code == HTTPStatus.OK:
                        text = _extract_text_from_response(response) or str(response.output if hasattr(response, 'output') else response)
                        if text:
                            yield from _stream_text_as_words(text)
                    else:
                        error_msg = f"API调用失败: {getattr(response, 'message', '未知错误')} (状态码: {response.status_code})"
                        logger.error(error_msg)
                        yield _send_sse_chunk(error_msg)
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"生成AI回答时出错: {str(e)}", exc_info=True)
                yield _send_sse_chunk(f"AI对话失败: {str(e)}")
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
    """
    构建提示词
    
    会在日志中打印完整的提示词内容，方便分析和调试
    """
    from models.meeting import Meeting
    from models.document import Document
    from services.document_service import DocumentService
    
    logger.info(f"[AI提示词构建] 开始构建提示词 - meeting_id: {meeting_id}, chat_history长度: {len(chat_history) if chat_history else 0}")
    
    prompt_parts = []
    documents_count = 0
    
    # 获取会议信息
    meeting = Meeting.query.get(meeting_id)
    if meeting:
        # 构建教师角色和教学范围限定
        role_parts = []
        role_parts.append("你是一个AI助手，一个专门用于辅助备课教学的机器人。你不是老师，你只是一个AI助手，虽然你非常擅长备课教学，但你是一个机器人。")
        
        if meeting.subject:
            role_parts.append(f"学科：{meeting.subject}")
        if meeting.grade:
            role_parts.append(f"年级：{meeting.grade}")
        if meeting.lesson_type:
            role_parts.append(f"备课类型：{meeting.lesson_type}")
        if meeting.description:
            role_parts.append(f"教学主题：{meeting.description}")
        
        if role_parts:
            prompt_parts.append("【教学范围限定】\n" + "\n".join(role_parts))
        
        # 获取已解析的备课资料（docx）
        documents = Document.query.filter_by(
            meeting_id=meeting_id,
            file_type='docx',
            status='completed'  # 只使用已解析完成的文档
        ).all()
        
        documents_count = len(documents)
        logger.info(f"[AI提示词构建] 找到 {documents_count} 个已解析完成的文档")
        
        if documents:
            doc_summaries = []
            
            for doc in documents:
                # 优先使用单独的 summary 字段（这是从备课资料中提取的核心信息点）
                if doc.summary:
                    doc_summaries.append(f"文档《{doc.original_filename}》的核心信息点：\n{doc.summary}")
                elif doc.parsed_content:
                    # 如果没有 summary 字段，使用前500字作为摘要（兼容旧数据）
                    summary_text = doc.parsed_content[:500] + "..." if len(doc.parsed_content) > 500 else doc.parsed_content
                    doc_summaries.append(f"文档《{doc.original_filename}》的内容摘要：\n{summary_text}")
            
            if doc_summaries:
                prompt_parts.append("【备课资料核心信息点】\n" + "\n\n".join(doc_summaries))
                prompt_parts.append("说明：以上是从备课资料中提取的核心信息点，请充分理解这些信息，并在回答时结合这些核心点提供专业的备课建议。")
    
    # 添加会议讨论记录
    if chat_history:
        prompt_parts.append("【会议讨论记录】\n" + chat_history)
    
    # 构建最终提示词
    if not prompt_parts:
        return "请为我总结一下会议内容。"
    
    # 添加指导性提示
    instruction = """请根据以上信息，特别是最后用户的问答给出信息。

【重要提示】
1. **明确身份定位**：你是一个AI助手/机器人，不是老师。你只是擅长备课教学，但你是机器人身份。不要使用任何不存在的举例，比如"你带过的学生"、"你上过的课"、"你的教学经验"等。你只是一个AI助手，基于提供的备课资料和讨论内容来提供建议。
2. **充分理解备课资料核心信息点**：这些是从备课资料中提取的关键信息，请深入理解并灵活运用
3. **结合教学范围限定**：在回答时要充分考虑学科、年级、备课类型等限制条件
4. **结合会议讨论内容**：根据当前的讨论记录，提供针对性的建议和回应
5. **提供专业建议**：基于备课资料的核心点和讨论内容，提供：
   - 教学重点和难点的分析
   - 教学方法和策略的建议
   - 与备课资料核心点的结合应用
   - 针对讨论中提出的问题的专业解答

【回答要求】
- **简洁明了**：直接说重点，避免冗余和啰嗦的表达
- **字数控制**：回答内容严格控制在 200-400 字之间
- **专业清晰**：用专业、清晰、有针对性的语言回答，确保建议与备课资料的核心信息点紧密结合
- **记住身份**：你是一个AI助手/机器人，不要编造任何不存在的个人经历或教学经验"""
    
    prompt = "\n\n".join(prompt_parts)
    prompt += "\n\n" + instruction
    
    # 打印详细的提示词，方便分析和调试
    logger.info("=" * 100)
    logger.info("[AI提示词构建] ========== 完整提示词内容 ==========")
    logger.info("=" * 100)
    logger.info(f"[AI提示词构建] 会议ID: {meeting_id}")
    logger.info(f"[AI提示词构建] 提示词总长度: {len(prompt)} 字符")
    logger.info(f"[AI提示词构建] 包含文档数量: {documents_count}")
    logger.info("-" * 100)
    logger.info("[AI提示词构建] 完整提示词内容（逐行显示）:")
    logger.info("-" * 100)
    # 分行打印，每行单独记录，便于阅读和分析
    for i, line in enumerate(prompt.split('\n'), 1):
        # 如果行太长，可以截断显示（但完整记录）
        display_line = line[:200] + "..." if len(line) > 200 else line
        logger.info(f"[AI提示词] [{i:4d}] {display_line}")
        if len(line) > 200:
            logger.debug(f"[AI提示词] [{i:4d}] (完整内容，长度: {len(line)}) {line}")
    logger.info("-" * 100)
    logger.info(f"[AI提示词构建] 提示词构建完成，共 {len(prompt.split(chr(10)))} 行")
    logger.info("=" * 100)
    
    return prompt

