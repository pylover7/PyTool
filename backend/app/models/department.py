from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .base import BaseModel, TimestampMixin


if TYPE_CHECKING:
    from .user import User


class DepartmentBase(BaseModel):
    name: str = Field(max_length=20, unique=True, description="部门名称")
    parentId: UUID | None = Field(default=None, nullable=True, description="父部门ID")
    sort: int = Field(default=0, description="排序")
    phone: str = Field(default=None, max_length=20, nullable=True, description="电话")
    principal: str = Field(default=None, max_length=20, nullable=True, description="负责人")
    email: str = Field(default=None, max_length=255, nullable=True, description="邮箱")
    status: int = Field(default=0, description="状态：启用/停用")
    remark: str = Field(default=None, max_length=500, nullable=True, description="备注信息")


class Department(DepartmentBase, TimestampMixin, table=True):
    users: list["User"] = Relationship(back_populates="department")


class DepartCreate(DepartmentBase):
    user: list = None


class DepartUpdate(SQLModel):
    id: str
    name: str
    parentId: UUID | None = None
    sort: int | None = None
    phone: str | None = None
    principal: str | None = None
    email: str | None = None
    status: int | None = None
    remark: str | None = None
