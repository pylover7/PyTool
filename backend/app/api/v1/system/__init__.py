from fastapi import APIRouter

from .user import userRouter
from .depart import departRouter
from .role import roleRouter
from .menu import menuRouter
from .api import apiRouter
from .monitor import monitorRouter

systemRouter = APIRouter()
systemRouter.include_router(userRouter, prefix="/user", tags=["系统用户模块"])
systemRouter.include_router(departRouter, prefix="/depart", tags=["系统部门模块"])
systemRouter.include_router(roleRouter, prefix="/role", tags=["系统角色模块"])
systemRouter.include_router(menuRouter, prefix="/menu", tags=["系统菜单模块"])
systemRouter.include_router(apiRouter, prefix="/api", tags=["系统接口模块"])
systemRouter.include_router(monitorRouter, prefix="/monitor", tags=["系统监控模块"])



__all__ = ["systemRouter"]
