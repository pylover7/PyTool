from datetime import datetime

import pytz


def convert_utc_to_local_time(utc_time_str: str, strip: str, tz: str = "Asia/Shanghai") -> datetime:
    """
    将 UTC 时间字符串转换为本地时间字符串

    :param utc_time_str: 时间字符串
    :param strip: 时间格式
    :param tz: 时区，默认为 "Asia/Shanghai"
    :return: 本地时间，类型为 datatime
    """
    # 将 UTC 时间字符串转换为 datetime 对象
    utc_time = datetime.strptime(utc_time_str, strip)

    # 创建一个时区对象，表示 UTC
    utc_tz = pytz.timezone(tz)

    # 将 UTC 时间对象标记为 UTC 时区
    utc_time = utc_tz.localize(utc_time)

    # 将 UTC 时间转换为北京时间（东八区）
    beijing_tz = pytz.timezone("Asia/Shanghai")
    beijing_time = utc_time.astimezone(beijing_tz)

    # 返回转换后的北京时间字符串
    return beijing_time