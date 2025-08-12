from datetime import datetime

from sqlmodel import SQLModel, Field


class CredentialsSchema(SQLModel):
    username: str = Field(..., description="用户名称")
    password: str = Field(..., description="密码")


class refreshTokenSchema(SQLModel):
    refreshToken: str = Field(..., description="刷新令牌")


class JWTReOut(SQLModel):
    accessToken: str
    refreshToken: str
    expires: str


class JWTOut(SQLModel):
    username: str
    avatar: str
    depart: str
    roles: list[str]
    accessToken: str
    refreshToken: str
    expires: str


class JWTPayload(SQLModel):
    user_id: str
    username: str
    is_superuser: bool
    exp: datetime
