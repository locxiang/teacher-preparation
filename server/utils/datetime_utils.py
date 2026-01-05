"""
时区工具函数
用于获取北京时间（UTC+8）
"""
from datetime import datetime, timezone, timedelta


def beijing_now():
    """
    获取当前北京时间（UTC+8）
    
    Returns:
        datetime: 当前北京时间的datetime对象（naive datetime，无时区信息）
    """
    # 获取UTC时间
    utc_now = datetime.now(timezone.utc)
    # 转换为北京时间（UTC+8）
    beijing_tz = timezone(timedelta(hours=8))
    beijing_time = utc_now.astimezone(beijing_tz)
    # 返回naive datetime（去掉时区信息），与数据库兼容
    return beijing_time.replace(tzinfo=None)

