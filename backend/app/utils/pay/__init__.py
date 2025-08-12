from app.settings.config import pay_config


def notify_url(name: str):
    """
    生成通知URL

    根据配置信息和提供的通知名称，构造一个通知URL

    参数:
    name (str): 通知的名称，用于构建URL的路径部分，如 wechat

    返回:
    str: 构建好的通知URL字符串
    """
    return f"{pay_config.get_config('base', 'notify')}/proxy/api/v1/base/notify/{name}"
