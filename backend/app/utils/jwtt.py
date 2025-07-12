import jwt

from app.models.login import JWTPayload
from app.settings import settings


def create_access_token(*, data: JWTPayload) -> str:
    """
    创建访问令牌

    :param data: 数据
    :return: 令牌
    """
    payload = data.model_dump().copy()
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> JWTPayload:
    """
    解码访问令牌

    :param token: 令牌
    :return: 数据
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return JWTPayload(**payload)
