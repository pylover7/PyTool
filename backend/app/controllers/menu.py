from app.core.crud import CRUDBase
from app.models import Menu, MenuCreate, MenuUpdate


class MenuController(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    def __init__(self):
        super().__init__(Menu)


menuController = MenuController()
