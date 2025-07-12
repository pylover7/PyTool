import re
from pydantic import BaseModel

import httpx
from fastapi import Request
import ipaddress

from app.settings.log import logger

api1 = "https://opendata.baidu.com/api.php?query={}&co=&resource_id=6006&oe=utf8"
api2 = "https://searchplugin.csdn.net/api/v1/ip/get?ip={}"

async def getIpAddress(ip: str) -> str:
    if ipaddress.ip_address(ip).is_private:
        return "内网IP"
    try:
        res = httpx.get(api2.format(ip))
        res.content.decode("utf-8")
        return res.json()["data"]["address"].replace(" ", "")
    except Exception as e:
        logger.error(f"获取IP地址失败，API2失效！")
        pass
    try:
        res = httpx.get(api1.format(ip))
        res.content.decode("utf-8")
        return res.json()["data"][0]["location"].replace(" ", "")
    except Exception as e:
        logger.error(f"获取IP地址失败，API1失效！")
        return ""


class SysBro(BaseModel):
    system: str
    browser: str


async def getReqSysBro(request: Request) -> SysBro:
    ua = request.headers.get("User-Agent")
    system = re.findall(r"\(([^;]+)", ua)[0][0:] or "未知系统"
    browser = re.findall(r"(Chrome|Edg|Safari|Firefox|MSIE|Trident)/", ua)[0] or "未知浏览器"
    return SysBro(system=system, browser=browser)

if __name__ == '__main__':
    print(getIpAddress("127.0.0.1"))

