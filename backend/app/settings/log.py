import sys
from pathlib import Path

from loguru import logger as loguru_logger

loginLogs = Path(__file__).parent.parent.parent.joinpath("logs", "login.log")
systemLogs = Path(__file__).parent.parent.parent.joinpath("logs", "system.log")
operationLogs = Path(__file__).parent.parent.parent.joinpath("logs", "operation.log")


class Logger:
    def __init__(self):
        self.logger = loguru_logger
        self.logger.remove()
        self.logger.add(
            sink=sys.stderr,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> |"
                   " <level>Logger: {extra[name]}</level> | <level>{message}</level>"
        )
        self.logger.add(
            sink=systemLogs,
            level="DEBUG",
            rotation="10 MB",
            encoding="utf-8",
            retention="10 days",
            compression="zip",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            filter=lambda record: record["extra"].get("name") == "system"
        )
        self.logger.add(
            sink=loginLogs,
            level="SUCCESS",
            rotation="10 MB",
            encoding="utf-8",
            retention="10 days",
            compression="zip",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra[user]} | "
                   "{extra[ip]} | {extra[ip_area]} | {extra[system]} | {extra[browser]} | <level>{message}</level>",
            filter=lambda record: record["extra"].get("name") == "login"
        )
        self.logger.add(
            sink=operationLogs,
            level="INFO",
            rotation="10 MB",
            encoding="utf-8",
            retention="10 days",
            compression="zip",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra[user]} | <level>{message}</level>",
            filter=lambda record: record["extra"].get("name") == "operation"
        )
        self.sysLogger = self.logger.bind(name="system")
        self.loginLogger = self.logger.bind(name="login")
        self.operationLogger = self.logger.bind(name="operation")

    def loginType(self, t: int):
        match t:
            case 0:
                return "账号登录"
            case 1:
                return "微信登录"
            case 2:
                return "QQ登录"
            case 3:
                return "手机号登录"

    def info(self, msg):
        self.sysLogger.info(msg)

    def debug(self, msg):
        self.sysLogger.debug(msg)

    def warning(self, msg):
        self.sysLogger.warning(msg)

    def error(self, msg):
        self.sysLogger.error(msg)

    def success(self, msg):
        self.sysLogger.success(msg)

    def loginSuccess(self, user: str, ip: str, ip_area: str, system: str, browser: str, behavior: int):
        """
        登录成功日志

        :param user: 用户
        :param ip: ip
        :param ip_area: 登录地点
        :param system: 操作系统
        :param browser: 浏览器类型
        :param behavior: 登录行为：0：账号/1：微信/2：QQ/3：电话登录 等
        """
        self.loginLogger.success(self.loginType(behavior), user=user, ip=ip, ip_area=ip_area, system=system, browser=browser)

    def loginFail(self, user: str, ip: str, ip_area: str, system: str, browser: str, behavior: int):
        """
        登录失败日志
        :param user: 用户
        :param ip: ip
        :param ip_area: 登录地点
        :param system: 操作系统
        :param browser: 浏览器类型
        :param behavior: 登录行为：0：账号/1：微信/2：QQ/3：电话登录 等
        """
        self.loginLogger.error(self.loginType(behavior), user=user, ip=ip, ip_area=ip_area, system=system, browser=browser)

    def operationInfo(self, user: str, msg: str):
        self.operationLogger.info(msg, user=user)

    def operationWarning(self, user: str, msg: str):
        self.operationLogger.warning(msg, user=user)

    def operationError(self, user: str, msg: str):
        self.operationLogger.error(msg, user=user)

logger = Logger()

if __name__ == '__main__':
    logger.operationError("dayezi", "test")
    logger.loginFail("dayezi", ip="xxx", ip_area="xxx", system="xxx", browser="xxx", behavior=0)
