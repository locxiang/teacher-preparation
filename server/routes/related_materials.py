"""
网络资料路由 - 根据对话内容自动搜索网上资料
使用 AI 提取关键词、SerpApi 官方 SDK 搜索、AI 打标签
"""
import json
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config import Config

try:
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

try:
    from serpapi import GoogleSearch, BaiduSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False

related_materials_bp = Blueprint('related_materials', __name__)
logger = logging.getLogger(__name__)


def _extract_search_keywords(chat_content: str) -> tuple[list[str], str]:
    """
    使用 AI 根据对话内容分析并总结搜索关键词。
    返回: (用于搜索的关键词列表, 用于展示的 AI 总结关键词)
    """
    if not DASHSCOPE_AVAILABLE or not Config.DASHSCOPE_API_KEY:
        words = chat_content.replace('，', ' ').replace('。', ' ').split()
        fallback = [w for w in words if len(w) > 1][:3] or [chat_content[:30]]
        return fallback, '、'.join(fallback)

    prompt = f"""你是一个备课会议助手。请根据以下备课会议对话内容，分析并总结出适合用于网上搜索资料的关键词。

要求：
1. 理解对话讨论的核心主题（如教学主题、学科概念、教学方法、课程标准等）
2. 总结为 2-4 个搜索关键词，用顿号「、」连接成一句
3. 关键词要精炼、便于搜索，例如：「分数教学、教学设计、案例分享」或「初中数学、课程标准、核心素养」

对话内容：
{chat_content[:1500]}

请直接输出总结后的搜索关键词（一句话，不要其他解释）："""

    try:
        response = Generation.call(
            api_key=Config.DASHSCOPE_API_KEY,
            model='qwen-turbo',
            prompt=prompt,
            max_tokens=80,
        )
        if response.status_code == 200:
            output = response.output or {}
            text = (output.get('text', '') or '').strip()
            if not text and isinstance(output, dict):
                choices = output.get('choices', [])
                if choices and isinstance(choices[0], dict):
                    msg = choices[0].get('message', {})
                    text = (msg.get('content', '') or '').strip()
            if text:
                # 解析：AI 可能用顿号、逗号、空格分隔
                normalized = text.replace('，', '、').replace('；', '、')
                keywords = [k.strip() for k in normalized.split('、') if k.strip()][:4]
                if not keywords:
                    keywords = [text[:30]]
                display_keyword = text[:60]  # 展示用，限制长度
                return keywords, display_keyword
    except Exception as e:
        logger.warning(f"AI 分析关键词失败: {e}")
    words = chat_content.replace('，', ' ').replace('。', ' ').split()
    fallback = [w for w in words if len(w) > 1][:3] or [chat_content[:30]]
    return fallback, '、'.join(fallback)


def _search_web(
    query: str, max_results: int = 6, engine: str = "baidu"
) -> tuple[list[dict], str | None]:
    """
    使用 SerpApi 官方 Python SDK 搜索。
    engine: "google" | "baidu"
    返回: (结果列表, 错误信息，成功时为 None)
    """
    api_key = (Config.SERPAPI_API_KEY or "").strip()
    if not api_key:
        return [], (
            "请配置 SERPAPI_API_KEY。在 serpapi.com 注册获取，.env 中设置 SERPAPI_API_KEY=你的key"
        )
    if not SERPAPI_AVAILABLE:
        return [], "请安装 SerpApi 依赖: pip install google-search-results"

    use_google = (engine or "baidu").lower() == "google"

    # 为教育备课场景增强搜索词，提高相关性
    enhanced_query = query
    if query and "教学" not in query and "教案" not in query and "备课" not in query:
        enhanced_query = f"{query} 教学 教案"

    if use_google:
        params = {
            "engine": "google",
            "q": enhanced_query,
            "google_domain": "google.com",
            "hl": "zh-cn",
            "gl": "cn",
            "num": max_results,
            "api_key": api_key,
        }
        SearchClass = GoogleSearch
    else:
        params = {
            "engine": "baidu",
            "q": enhanced_query,
            "api_key": api_key,
        }
        if max_results:
            params["rn"] = min(max_results, 50)
        SearchClass = BaiduSearch

    try:
        search = SearchClass(params)
        data = search.get_dict()
        organic = data.get("organic_results") or data.get("organic") or []

        if not organic and enhanced_query != query:
            logger.info(f"[网络资料] 增强查询无结果，回退到原始关键词: {query}")
            params["q"] = query
            search2 = SearchClass(params)
            data2 = search2.get_dict()
            organic = data2.get("organic_results") or data2.get("organic") or []

        if not organic:
            logger.info(f"[网络资料] SerpApi 返回空结果, engine={engine}, query={enhanced_query}")

        items = []
        for r in organic[:max_results]:
            link = r.get("link") or r.get("url", "")
            if not link:
                continue
            items.append({
                "title": r.get("title", ""),
                "url": link,
                "snippet": r.get("snippet", ""),
            })
        return items, None
    except Exception as e:
        err_str = str(e)
        logger.warning(f"[网络资料] SerpApi 搜索失败 (engine={engine}): {e}")
        if "403" in err_str or "Invalid API key" in err_str.lower():
            return [], (
                "搜索服务返回 403：API Key 无效或额度已用尽。"
                "请到 serpapi.com 检查 Key 和用量，更新 .env 中的 SERPAPI_API_KEY"
            )
        return [], f"搜索失败: {err_str[:80]}"


def _add_tags_with_ai(items: list[dict], chat_context: str) -> list[dict]:
    """使用 AI 为每条结果打上业务相关标签"""
    if not items or not DASHSCOPE_AVAILABLE or not Config.DASHSCOPE_API_KEY:
        for item in items:
            item.setdefault('tags', ['网络资料'])
        return items

    # 构建标签候选（业务人员能理解的词汇）
    tag_candidates = [
        '教学策略', '课程标准', '案例分享', '学科知识', '教学资源',
        '教学设计', '课堂活动', '评价方法', '教材解读', '备课参考',
    ]

    prompt = f"""根据备课会议对话背景，为以下每条网上资料打 1-2 个标签。
标签从以下候选中选择：{', '.join(tag_candidates)}
若都不合适，可自拟一个简短标签（2-4字）。

对话背景摘要：{chat_context[:300]}

资料列表（每行格式：标题 | 摘要）：
"""
    for i, item in enumerate(items[:8], 1):
        prompt += f"\n{i}. {item.get('title', '')} | {item.get('snippet', '')[:80]}"

    prompt += """

请输出 JSON 数组，每项对应一条资料的标签数组，如：["教学策略","案例分享"]
只输出 JSON，不要其他内容。"""

    try:
        response = Generation.call(
            api_key=Config.DASHSCOPE_API_KEY,
            model='qwen-turbo',
            prompt=prompt,
            max_tokens=200,
        )
        if response.status_code == 200:
            output = response.output or {}
            text = (output.get('text', '') or '').strip()
            if not text and isinstance(output, dict):
                choices = output.get('choices', [])
                if choices and isinstance(choices[0], dict):
                    msg = choices[0].get('message', {})
                    text = (msg.get('content', '') or '').strip()
            # 尝试解析 JSON
            text = text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(text)
            if isinstance(parsed, list):
                for i, item in enumerate(items):
                    if i < len(parsed) and isinstance(parsed[i], list):
                        item['tags'] = parsed[i][:2]
                    else:
                        item['tags'] = ['网络资料']
            else:
                for item in items:
                    item.setdefault('tags', ['网络资料'])
        else:
            for item in items:
                item.setdefault('tags', ['网络资料'])
    except Exception as e:
        logger.warning(f"AI 打标签失败: {e}")
        for item in items:
            item.setdefault('tags', ['网络资料'])
    return items


@related_materials_bp.route('/search', methods=['POST'])
@jwt_required()
def search_related_materials():
    """
    根据对话内容搜索网络资料
    请求体: { "messages": [ { "role": "user"|"assistant", "content": "..." } ] }
    返回: { "success": true, "data": [ { "title", "url", "snippet", "tags" } ] }
    """
    try:
        data = request.get_json() or {}
        messages = data.get("messages", [])
        engine = (data.get("engine") or "baidu").lower()
        if engine not in ("google", "baidu"):
            engine = "baidu"
        if not messages or not isinstance(messages, list):
            return jsonify({'success': False, 'message': '请提供对话内容', 'data': []}), 400

        # 合并最近对话内容
        chat_parts = []
        for m in messages[-10:]:
            content = (m.get('content') or '').strip()
            if content:
                role = m.get('role', 'user')
                prefix = '用户' if role == 'user' else 'AI'
                chat_parts.append(f"{prefix}: {content}")
        chat_content = '\n'.join(chat_parts)
        if not chat_content.strip():
            return jsonify({'success': True, 'keyword': '', 'data': [], 'message': '对话内容为空'})

        # 1. AI 根据对话分析并总结搜索关键词
        keywords, display_keyword = _extract_search_keywords(chat_content)
        logger.info(f"[网络资料] AI 总结关键词: {display_keyword}, 用于搜索: {keywords}")

        # 2. 搜索（优先用多关键词组合，提高召回率）
        query = ' '.join(keywords[:2]) if len(keywords) >= 2 else (keywords[0] if keywords else chat_content[:50])
        if not query:
            return jsonify({'success': True, 'keyword': '', 'data': []})

        raw_results, search_error = _search_web(query.strip(), max_results=6, engine=engine)
        if search_error:
            return jsonify({
                'success': False,
                'message': search_error,
                'keyword': display_keyword,
                'data': [],
            }), 200  # 200 以便前端能解析并显示错误信息
        if not raw_results:
            return jsonify({'success': True, 'keyword': display_keyword, 'data': []})

        # 3. AI 打标签
        items = _add_tags_with_ai(raw_results, chat_content)

        return jsonify({
            'success': True,
            'keyword': display_keyword,
            'data': [
                {
                    'title': it.get('title', ''),
                    'url': it.get('url', ''),
                    'snippet': (it.get('snippet', '') or '')[:120],
                    'tags': it.get('tags', ['网络资料']),
                }
                for it in items
            ],
        })
    except Exception as e:
        logger.exception("网络资料搜索失败")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': [],
        }), 500
