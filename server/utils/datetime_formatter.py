"""
时间格式化工具
"""
from datetime import timezone, timedelta


def format_datetime_to_beijing(dt_str: str) -> str:
    """
    将 ISO 格式时间转换为 'YYYY-MM-DD HH:MM:SS' 格式（北京时间）
    
    Args:
        dt_str: ISO 格式的时间字符串
        
    Returns:
        格式化的时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'
    """
    try:
        from dateutil import parser
        dt = parser.parse(dt_str)
        # 如果有时区信息，转换为北京时间（UTC+8）
        if dt.tzinfo is not None:
            beijing_tz = timezone(timedelta(hours=8))
            dt = dt.astimezone(beijing_tz)
        # 格式化为 "YYYY-MM-DD HH:MM:SS"
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        # 如果解析失败，尝试简单的字符串替换
        return dt_str.replace('T', ' ').split('.')[0].split('+')[0]

