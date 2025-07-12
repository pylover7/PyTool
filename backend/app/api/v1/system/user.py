import time
from pathlib import Path

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from sqlmodel import col, and_

from app.core.dependency import SessionDep
from app.controllers.role import roleController
from app.controllers.user import userController
from app.models.base import Success, SuccessExtra
from app.models.user import UserCreate, UserUpdate, User, UserFiter, UserResetPwd, UserAvatar, UpdateStatus, \
    UpdateUserRoles
from app.settings.log import logger
from app.settings import settings
from app.utils import base_decode
from app.utils.password import get_password_hash, md5_encrypt

userRouter = APIRouter()


@userRouter.post("/add", summary="新增用户")
async def create_user(
        session: SessionDep,
        data: UserCreate,
):
    user = await userController.get_user_by_name(session, data.username)
    if user or (data.username == "admin"):
        raise HTTPException(
            status_code=400,
            detail="该用户已存在！",
        )
    try:
        await userController.create(session, data)
        return Success(msg="用户创建成功！")
    except Exception as e:
        logger.error(f"用户创建失败：{e}")
        raise HTTPException(status_code=400, detail="用户创建失败！")


@userRouter.delete("/delete", summary="删除用户")
async def delete_user(
        session: SessionDep,
        data: list[str]
):
    try:
        await userController.delete(session, data)
        logger.warning(f"用户ID: {data} 已被删除")
        return Success(msg="Deleted Successfully")
    except Exception as e:
        logger.error(f"用户删除失败：{e}")
        raise HTTPException(status_code=400, detail="用户删除失败！")


@userRouter.get("/get", summary="查看用户")
async def get_user(
        session: SessionDep,
        id: str = Query(..., description="用户ID"),
):
    user_obj: User = await userController.get(session, id)
    user_dict = await user_obj.to_dict(exclude_fields=["password"])
    return Success(data=user_dict)


@userRouter.post("/list", summary="查看用户列表")
async def list_user(
        session: SessionDep,
        data: UserFiter,
        currentPage: int = Query(1, description="页码"),
        pageSize: int = Query(15, description="每页数量"),
):
    where = []
    if data.username:
        where.append(User.username == data.username)
    if data.email:
        where.append(User.email == data.email)
    if data.departId:
        where.append(User.department_id == data.departId)
    if len(where) > 0:
        where = and_(*where, )
    else:
        where = None
    order = col(User.id).desc()
    total, user_objs = await userController.list(
        session,
        currentPage,
        pageSize,
        where,
        order
    )
    total: int
    user_objs: list[User]
    data = []
    for obj in user_objs:
        obj_dict = await obj.to_dict(exclude_fields=["password"])
        obj_dict["roleIds"] = [item.id.__str__() for item in obj.roles]
        data.append(obj_dict)
    return SuccessExtra(data=data, total=total, currentPage=currentPage, pageSize=pageSize)


@userRouter.post("/update", summary="更新用户")
async def update_user(
        session: SessionDep,
        data: UserUpdate,
):
    user = await userController.get_user_by_name(session, data.username)
    del data.username
    await userController.update(session, user.id, data)
    return Success(msg="用户信息更新成功！")


@userRouter.post("/updateAvatar", summary="更新用户头像")
async def update_avatar(
        session: SessionDep,
        data: UserAvatar,
):
    user = await userController.get(session, data.id)
    avatar_name = f"{md5_encrypt(str(user.id))}_{time.time_ns()}.{data.avatar.base64.split(';')[0].split('/')[-1]}"
    avatar_path = Path.joinpath(Path(settings.AVATAR_PATH), avatar_name)
    with open(avatar_path, "wb") as f:
        imgData = base_decode(data.avatar.base64.split(",")[1])
        f.write(imgData)
    user.avatar = avatar_name
    session.add(user)
    session.commit()
    return Success(msg="用户头像信息更新成功！")


@userRouter.post("/updateRoles", summary="更新用户角色")
async def update_roles(
        session: SessionDep,
        data: UpdateUserRoles,
):
    user = await userController.get(session, data.id)
    roleList = []
    for role_id in data.roleIds:
        role = await roleController.get(session, role_id)
        roleList.append(role)

    user.roles = roleList
    session.add(user)
    session.commit()
    return Success(msg="用户角色信息更新成功！")


@userRouter.post("/updateStatus", summary="更新用户状态")
async def update_status(session: SessionDep, data: UpdateStatus):
    user = await userController.get(session, data.id)
    user.status = data.status
    session.add(user)
    session.commit()
    return Success(msg="用户状态更新成功！")


@userRouter.post("/resetPwd", summary="重置用户密码")
async def reset_pwd(
        session: SessionDep,
        data: UserResetPwd,
):
    user = await userController.get(session,data.id)
    user.password = get_password_hash(data.newPwd)
    session.add(user)
    session.commit()
    return Success(msg="密码重置成功！")
