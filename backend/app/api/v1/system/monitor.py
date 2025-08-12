from fastapi import APIRouter, Query

from app.controllers.user import userController
from app.core.ctx import CTX_USER_ID
from app.core.dependency import SessionDep
from app.models import Success, SuccessExtra
from app.settings.log import loginLogs, operationLogs, systemLogs, logger
from app.utils.localTime import convert_utc_to_local_time

monitorRouter = APIRouter()


@monitorRouter.post("/getLoginLogs", summary="获取登录日志")
async def get_login_logs(
        data: dict,
        currentPage: int = Query(1, description="页码"),
        pageSize: int = Query(15, description="每页数量"),
):
    # 读取 loginLog 下的文件，按照逆序读取，根据currentPage 和 pageSize 分页，并计算总数量total
    logList = []
    with open(loginLogs, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # 对读取的日志先经过username和status，以及startTime和endTime 过滤
        if data["username"]:
            lines = [line for line in lines if data["username"] in line]
        if data["status"]:
            newLines = []
            for line in lines:
                if data["status"] == "1" and "SUCCESS" in line:
                    newLines.append(line)
                elif data["status"] == "0" and "ERROR" in line:
                    newLines.append(line)
            lines = newLines
        if data["loginTime"] is not None and len(data["loginTime"]) > 1:
            lines = [line for line in lines if
                     convert_utc_to_local_time(
                         data["loginTime"][0], "%Y-%m-%dT%H:%M:%S.%fZ", "UTC")
                     <= convert_utc_to_local_time(line.split("|")[0].strip(), "%Y-%m-%d %H:%M:%S.%f")
                     <= convert_utc_to_local_time(data["loginTime"][1], "%Y-%m-%dT%H:%M:%S.%fZ", "UTC")]

        total = len(lines)
        if total == 0:
            return SuccessExtra(data=logList, total=total,
                                currentPage=currentPage, pageSize=pageSize)
        start_index = total - pageSize * (currentPage - 1)
        end_index = start_index - pageSize
        if end_index < 0:
            end_index = 0
        for i in range(start_index, end_index, -1):
            # 分割日志行
            parts = lines[i - 1].strip().split('|')
            # 构建字典
            log_dict = {
                "username": parts[2].strip(),
                "status": 1 if parts[1].strip() == "SUCCESS" else 0,
                "ip": parts[3].strip(),
                "loginTime": parts[0].strip(),
                "address": parts[4].strip(),
                "system": parts[5].strip(),
                "browser": parts[6].strip(),
                "behavior": parts[7].strip(),
            }
            logList.append(log_dict)
    return SuccessExtra(data=logList, total=total,
                        currentPage=currentPage, pageSize=pageSize)


@monitorRouter.get("/clearLoginLogs", summary="清除登录日志")
async def clear_login_logs(session: SessionDep):
    user = await userController.get(session, CTX_USER_ID.get())
    with open(loginLogs, "w", encoding="utf-8") as f:
        f.write("")
    logger.operationError(user.username, "清除登录日志")
    return Success(msg="清除成功！")


@monitorRouter.post("/getOperationLogs", summary="获取操作日志")
async def get_operation_logs(
        data: dict,
        currentPage: int = Query(1, description="页码"),
        pageSize: int = Query(15, description="每页数量"),
):
    # 读取 operationLog 下的文件，按照逆序读取，根据currentPage 和 pageSize 分页，并计算总数量total
    logList = []
    with open(operationLogs, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # 对读取的日志先经过username和status，以及startTime和endTime 过滤
        if data["username"]:
            lines = [line for line in lines if data["username"] in line]
        if data["level"]:
            newLines = []
            for line in lines:
                if data["level"] == "1" and "INFO" in line:
                    newLines.append(line)
                elif data["level"] == "2" and "WARNING" in line:
                    newLines.append(line)
                elif data["level"] == "0" and "ERROR" in line:
                    newLines.append(line)
            lines = newLines
        if data["operatingTime"] is not None and len(
                data["operatingTime"]) > 1:
            lines = [line for line in lines if
                     convert_utc_to_local_time(
                         data["operatingTime"][0], "%Y-%m-%dT%H:%M:%S.%fZ", "UTC")
                     <= convert_utc_to_local_time(line.split("|")[0].strip(), "%Y-%m-%d %H:%M:%S.%f")
                     <= convert_utc_to_local_time(data["operatingTime"][1], "%Y-%m-%dT%H:%M:%S.%fZ", "UTC")]
        total = len(lines)
        if total == 0:
            return SuccessExtra(data=logList, total=total,
                                currentPage=currentPage, pageSize=pageSize)

        start_index = total - pageSize * (currentPage - 1)
        end_index = start_index - pageSize
        if end_index < 0:
            end_index = 0
        for i in range(start_index, end_index, -1):
            # 分割日志行
            parts = lines[i - 1].strip().split('|')
            # 构建字典
            match parts[1].strip():
                case "INFO":
                    level = 1
                case "WARNING":
                    level = 2
                case "ERROR":
                    level = 0

            log_dict = {
                "username": parts[2].strip(),
                "operatingTime": parts[0].strip(),
                "level": level,
                "summary": parts[3].strip(),
            }
            logList.append(log_dict)
    return SuccessExtra(data=logList, total=total,
                        currentPage=currentPage, pageSize=pageSize)


@monitorRouter.get("/clearOperationLogs", summary="清除操作日志")
async def clear_operation_logs(session: SessionDep):
    user = await userController.get(session, CTX_USER_ID.get())
    with open(operationLogs, "w", encoding="utf-8") as f:
        f.write("")
    logger.operationError(user.username, "清除操作日志")
    return Success(msg="清除成功！")


@monitorRouter.post("/getSystemLogs", summary="获取系统日志")
async def get_system_logs(
        data: dict,
        currentPage: int = Query(1, description="页码"),
        pageSize: int = Query(15, description="每页数量"),
):
    # 读取 systemLogs 下的文件，按照逆序读取，根据currentPage 和 pageSize 分页，并计算总数量total
    logList = []
    with open(systemLogs, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if data["level"]:
            newLines = []
            for line in lines:
                if data["level"] == "0" and "DEBUG" in line:
                    newLines.append(line)
                elif data["level"] == "1" and "INFO" in line:
                    newLines.append(line)
                elif data["level"] == "2" and "WARNING" in line:
                    newLines.append(line)
                elif data["level"] == "3" and "ERROR" in line:
                    newLines.append(line)
            lines = newLines
        # 对读取的日志先经过username和status，以及startTime和endTime 过滤
        if data["systemTime"] is not None and len(data["systemTime"]) > 1:
            lines = [line for line in lines if
                     convert_utc_to_local_time(
                         data["systemTime"][0], "%Y-%m-%dT%H:%M:%S.%fZ", "UTC")
                     <= convert_utc_to_local_time(line.split("|")[0].strip(), "%Y-%m-%d %H:%M:%S.%f")
                     <= convert_utc_to_local_time(data["systemTime"][1], "%Y-%m-%dT%H:%M:%S.%fZ", "UTC")]

        total = len(lines)
        if total == 0:
            return SuccessExtra(data=logList, total=total,
                                currentPage=currentPage, pageSize=pageSize)

        start_index = total - pageSize * (currentPage - 1)
        end_index = start_index - pageSize
        if end_index < 0:
            end_index = 0
        for i in range(start_index, end_index, -1):
            # 分割日志行
            parts = lines[i - 1].strip().split('|')

            match parts[1].strip():
                case "DEBUG":
                    level = 0
                case "INFO":
                    level = 1
                case "WARNING":
                    level = 2
                case "ERROR":
                    level = 3
            # 构建字典
            log_dict = {
                "systemTime": parts[0].strip(),
                "level": level,
                "message": parts[2].strip(),
            }
            logList.append(log_dict)
    return SuccessExtra(data=logList, total=total,
                        currentPage=currentPage, pageSize=pageSize)


@monitorRouter.get("/clearSystemLogs", summary="清除系统日志")
async def clear_system_logs(session: SessionDep):
    user = await userController.get(session, CTX_USER_ID.get())
    with open(systemLogs, "w", encoding="utf-8") as f:
        f.write("")
    logger.operationError(user.username, "清除系统日志")
    return Success(msg="清除成功！")
