from sqlmodel import Session

from app.core.crud import CRUDBase
from app.models import Role, RoleCreate, RoleUpdate
from app.controllers.menu import menuController
from app.controllers.api import apiController


class RoleController(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(Role)

    async def updateMenus(self, session: Session, id: str, menuIds: list[str]):
        role_obj = await self.get(session, id)
        role_obj.menus.clear()
        for item in menuIds:
            menu_obj = await menuController.get(session, item)
            role_obj.menus.append(menu_obj)
        session.add(role_obj)
        session.commit()

    async def updateApis(self, session: Session, id: str, apiIds: list[str]):
        role_obj = await self.get(session, id)
        role_obj.apis.clear()
        for item in apiIds:
            if "/" in item:
                continue
            api_obj = await apiController.get(session, item)
            role_obj.apis.append(api_obj)
        session.add(role_obj)
        session.commit()


roleController = RoleController()
