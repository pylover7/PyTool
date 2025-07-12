from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

from .base import BaseModel, TimestampMixin
from .link import UserRoleLink, RoleMenuLink, RoleApiLink


if TYPE_CHECKING:
    from . import Menu, Api, User


class RoleCreate(SQLModel):
    name: str = Field(max_length=20, unique=True, description="角色名称")
    code: str = Field(max_length=20, unique=True, description="角色编码")
    status: int = Field(default=0, description="状态：启用/停用")
    remark: str = Field(default=None, max_length=500, nullable=True, description="角色描述")


class Role(BaseModel, RoleCreate, TimestampMixin, table=True):
    menus: list["Menu"] = Relationship(back_populates="roles", link_model=RoleMenuLink)
    apis: list["Api"] = Relationship(back_populates="roles", link_model=RoleApiLink)
    users: list["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)

class RoleUpdate(BaseModel):
    name: str | None
    code: str | None
    remark: str | None

class UpdateRoleStatus(BaseModel):
    status: int

class RoleFilter(SQLModel):
    name: str | None
    code: str | None
    status: str | None

class UpdateRoleAuth(BaseModel):
    menuUpdate: bool
    menuIds: list[str]
    apiUpdate: bool
    apiIds: list[str]
