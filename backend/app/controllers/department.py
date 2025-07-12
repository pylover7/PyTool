from sqlmodel import Session

from app.core.crud import CRUDBase
from app.models import User, Department, DepartCreate, DepartUpdate


class DepartmentController(CRUDBase[Department, DepartCreate, DepartUpdate]):
    def __init__(self):
        super().__init__(Department)

    def get_all_name(self, session: Session, user: User) -> str:
        """
        获取所有部门名称

        :param session: 数据库会话
        :param user: 用户
        :return: 用户的部门全称
        """
        depart = user.department
        departFullName = ""
        while depart.parentId != 0:
            departFullName = depart.name + departFullName
            depart = session.get(Department, depart.parentId)
        return departFullName


deptController = DepartmentController()
