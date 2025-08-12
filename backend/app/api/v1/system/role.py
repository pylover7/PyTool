from fastapi import APIRouter
from fastapi.params import Query
from sqlalchemy import and_
from sqlmodel import col

from app.controllers.role import roleController
from app.core.dependency import SessionDep
from app.models import RoleCreate, Success, RoleFilter, Role, SuccessExtra, RoleUpdate, UpdateRoleStatus, BaseModel, \
    UpdateRoleAuth

roleRouter = APIRouter()


@roleRouter.post("/add", summary="添加角色")
async def add_role(session: SessionDep, data: RoleCreate):
    role_obj = await roleController.create(session, data)
    result = await role_obj.to_dict()
    return Success(msg="角色添加成功！", data=result)


@roleRouter.post("/delete", summary="删除角色")
async def delete_role(session: SessionDep, data: list[str]):
    await roleController.delete(session, data)


@roleRouter.post("/list", summary="获取角色列表")
async def role_list(
        session: SessionDep,
        currentPage: int = Query(1, description="页码"),
        pageSize: int = Query(15, description="每页数量"),
        data: RoleFilter | None = None
):
    where = []
    if data.name:
        where.append(col(Role.name) == data.name)
    if data.code:
        where.append(col(Role.code) == data.code)
    if data.status:
        where.append(col(Role.status) == int(data.status))
    if len(where) > 0:
        where = and_(*where, )
    else:
        where = None
    total, role_obj = await roleController.list(session, currentPage, pageSize, where)
    total: int
    role_obj: list[Role]
    result = []
    for item in role_obj:
        role_dict = await item.to_dict()
        result.append(role_dict)
        role_dict["userCount"] = len(item.users)
    return SuccessExtra(msg="角色列表查询成功！", data=result, total=total,
                        currentPage=currentPage, pageSize=pageSize)


@roleRouter.get("/all", summary="获取所有角色")
async def role_all(session: SessionDep):
    role_obj = await roleController.all(session)
    result = [await item.to_dict() for item in role_obj]
    return Success(msg="角色列表查询成功！", data=result)


@roleRouter.post("/update", summary="修改角色信息")
async def update_role(session: SessionDep, data: RoleUpdate):
    await roleController.update(session, data.id, data)
    return Success(msg="角色信息修改成功！")


@roleRouter.post("/updateStatus", summary="修改角色状态")
async def update_role_status(session: SessionDep, data: UpdateRoleStatus):
    await roleController.update(session, data.id, data)
    return Success(msg="角色状态修改成功！")


@roleRouter.post("/getRoleAuth", summary="获取角色对应菜单列表和api列表")
async def get_role_auth(session: SessionDep, data: BaseModel):
    role_obj = await roleController.get(session, data.id)
    result = {
        "menus": [item.id.__str__() for item in role_obj.menus],
        "apis": [item.id.__str__() for item in role_obj.apis]
    }
    return Success(msg="角色权限查询成功！", data=result)


@roleRouter.post("/updateRoleAuth", summary="修改角色对应菜单列表和api列表")
async def update_role_auth(session: SessionDep, data: UpdateRoleAuth):
    if data.menuUpdate:
        await roleController.updateMenus(session, data.id, data.menuIds)
    elif data.apiUpdate:
        await roleController.updateApis(session, data.id, data.apiIds)
    return Success(msg="角色权限修改成功！")
