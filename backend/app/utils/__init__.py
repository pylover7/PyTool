import base64
import string
import random
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import emails
import jwt
from jwt.exceptions import JWTException

from app.models import Menu
from app.settings import settings
from app.settings.log import logger


@dataclass
class EmailData:
    html_content: str
    subject: str


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"])
        return str(decoded_token["sub"])
    except JWTException:
        return None


def base_decode(data: str) -> bytes:
    if len(data) % 3 == 1:
        data += "=="
    elif len(data) % 3 == 2:
        data += "="
    return base64.b64decode(data)


def generate_uuid(name: str) -> uuid.UUID:
    name = name + str(time.time_ns())
    return uuid.uuid5(uuid.NAMESPACE_DNS, name)


def now(s: int = 1) -> str | datetime | float:
    """
    获取当前时间，形参取值
        - 0: datatime格式
        - 1: xxxx-xx-xx xx:xx:xx 字符串格式
        - 2: 浮点类型时间戳格式

    :param s: 数字

    :return: 当前日期时间
    """
    today = datetime.now()
    match s:
        case 0:
            return today
        case 1:
            return today.strftime("%Y-%m-%d %H:%M:%S")
        case 2:
            return today.timestamp()
        case 3:
            return today.strftime("%Y%m%d%H%M%S")


async def menuTree(p_menu: dict, menus: list[Menu]) -> dict:
    """
    子菜单递归排序

    :param p_menu: 父菜单
    :param menus: 菜单列表
    :return: 子菜单排序后的父菜单
    """
    for menuItem in menus:
        if menuItem.parentId.__str__() == p_menu["id"]:
            # roles = await menu.roles.all().values_list("code", flat=True)
            children_menu = await menuItem.to_dict()
            children_menu["children"] = []
            children_menu["meta"] = {}
            children_menu["meta"]["title"] = children_menu["title"]
            children_menu["meta"]["icon"] = children_menu["icon"]
            children_menu["meta"]["extraIcon"] = children_menu["extraIcon"]
            children_menu["meta"]["showLink"] = children_menu["showLink"]
            children_menu["meta"]["showParent"] = children_menu["showParent"]
            # children_menu["meta"]["roles"] = roles
            children_menu["meta"]["auths"] = children_menu["auths"]
            children_menu["meta"]["keepAlive"] = children_menu["keepAlive"]
            children_menu["meta"]["frameSrc"] = children_menu["frameSrc"]
            children_menu["meta"]["frameLoading"] = children_menu["frameLoading"]
            children_menu["meta"]["frameLoading"] = children_menu["frameLoading"]
            children_menu["meta"]["hiddenTag"] = children_menu["hiddenTag"]
            children_menu["meta"]["dynamicLevel"] = children_menu["dynamicLevel"]
            children_menu["meta"]["activePath"] = children_menu["activePath"]
            children_menu["meta"]["transition"] = {}
            children_menu["meta"]["transition"]["name"] = children_menu["transitionName"]
            children_menu["meta"]["transition"]["enterTransition"] = children_menu["enterTransition"]
            children_menu["meta"]["transition"]["leaveTransition"] = children_menu["leaveTransition"]

            p_menu["children"].append(children_menu)

    p_menu["children"].sort(key=lambda x: x["rank"])
    if len(p_menu["children"]) == 0:
        del p_menu["children"]
        return p_menu
    for i, v in enumerate(p_menu["children"]):
        p_menu["children"][i] = await menuTree(v, menus)
    return p_menu


def random_string(length: int, prefix: str = ""):
    letters = string.ascii_letters
    code = prefix + "-" + "".join(random.choice(letters)
                                  for i in range(length))
    return code
