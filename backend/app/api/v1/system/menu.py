from fastapi import APIRouter

from app.controllers.menu import menuController
from app.core.dependency import SessionDep
from app.models import MenuCreate, Success, MenuUpdate

menuRouter = APIRouter()


@menuRouter.post("/add", summary="添加菜单")
async def add_menu(session: SessionDep, data: MenuCreate):
    menu_obj = await menuController.create(session, data)
    result = await menu_obj.to_dict()
    return Success(msg="菜单添加成功！", data=result)


@menuRouter.post("/delete", summary="删除菜单")
async def delete_menu(session: SessionDep, data: list[str]):
    await menuController.delete(session, data)
    return Success(msg="菜单删除成功！")


@menuRouter.get("/all", summary="获取菜单列表")
async def menu_list(session: SessionDep):
    menu_obj = await menuController.all(session)
    result = [await item.to_dict() for item in menu_obj]
    return Success(msg="菜单列表查询成功！", data=result)


@menuRouter.post("/update", summary="修改菜单信息")
async def update_menu(session: SessionDep, data: MenuUpdate):
    await menuController.update(session, data.id, data)
    return Success(msg="菜单信息修改成功！")
