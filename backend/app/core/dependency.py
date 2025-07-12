import jwt
from collections.abc import Generator
from sqlmodel import Session
from typing import Annotated
from fastapi import Depends, Header, HTTPException, Request

from app.controllers.user import userController
from app.core.database import engine
from app.core.ctx import CTX_USER_ID
from app.models import Role, User
from app.settings import settings
from app.settings.log import logger


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


class AuthControl:
    @classmethod
    async def is_authed(cls, session: SessionDep,
                        authorization: str = Header(..., description="token验证")):
        try:
            token = authorization.split(" ")[1]
            decode_data = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=settings.JWT_ALGORITHM)
            user_id: str = decode_data.get("user_id")
            CTX_USER_ID.set(user_id)
            user = await userController.get(session, user_id)
            if not user:
                raise HTTPException(status_code=401, detail="验证失败！！！")
            if user.is_superuser:  # 超级管理员不验证状态
                return user
            if not user.status:
                raise HTTPException(status_code=400, detail="用户已被禁用")
            for item in user.roles:
                if not item.status:
                    raise HTTPException(status_code=400, detail="用户已被禁用")
            return user
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="无效的Token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="登录已过期")


class PermissionControl:
    @classmethod
    async def has_permission(cls, request: Request, current_user: User = Depends(
            AuthControl.is_authed)) -> None:
        if current_user.is_superuser:
            return
        method = request.method
        path = request.url.path
        roles: list[Role] = current_user.roles
        if not roles:
            raise HTTPException(status_code=403,
                                detail="The user is not bound to a role")
        apis = [role.apis for role in roles]
        permission_apis = list(set((api.method, api.path)
                               for api in sum(apis, [])))
        # path = "/api/v1/auth/userinfo"
        # method = "GET"
        if (method, path) not in permission_apis:
            logger.debug(
                f"已禁止用户 {
                    current_user.username} 访问 {method} {path} 接口")
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied method:{method} path:{path}")
        else:
            logger.debug(
                f"已允许用户 {
                    current_user.username} 访问 {method} {path} 接口")


DependAuth = Depends(AuthControl.is_authed)
DependPermission = Depends(PermissionControl.has_permission)
