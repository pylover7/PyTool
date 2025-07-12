from fastapi import APIRouter

from app.models import Success
from app.settings.config import base_config

paySetRouter = APIRouter()

@paySetRouter.get("/get/{species}", summary="支付设置获取")
async def pay_setting(species: str):
    match species:
        case "email":
            result = {
                "host": base_config.get_config("email", "host"),
                "port": int(base_config.get_config("email", "port")),
                "username": base_config.get_config("email", "username"),
                "sender": base_config.get_config("email", "sender"),
            }
            return Success(data=result)
        case "wechat":
            result = {
                "appid": base_config.get_config("wechat", "appid"),
                "mchid": base_config.get_config("wechat", "mchid"),
                "key": base_config.get_config("wechat", "key"),
                "notify_url": base_config.get_config("wechat", "notify_url"),
                "cert_path": base_config.get_config("wechat", "cert_path"),
            }
            return Success(data=result)
        case _:
            return Success(msg="获取成功！")

@paySetRouter.post("/set/{species}", summary="支付设置更新")
async def pay_setting(species: str, data: dict):
    match species:
        case "email":
            base_config.set_config("email", "host", data["host"])
            base_config.set_config("email", "port", data["port"])
            base_config.set_config("email", "username", data["username"])
            base_config.set_config("email", "password", data["password"])
            base_config.set_config("email", "sender", data["sender"])
            return Success(msg="设置成功！")
