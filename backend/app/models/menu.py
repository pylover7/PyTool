from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from .base import BaseModel, TimestampMixin
from .link import RoleMenuLink


if TYPE_CHECKING:
    from app.models import Role


class MenuCreate(SQLModel):
    parentId: UUID | None = Field(default=None, nullable=True, description="父菜单ID")
    menuType: int = Field(default=0, description="菜单类型（0代表菜单、1代表iframe、2代表外链、3代表按钮）")
    title: str = Field(max_length=20, description="菜单名称")
    name: str = Field(max_length=50, description="路由名称必须唯一")
    path: str = Field(max_length=100, description="菜单路径")
    component: str = Field(max_length=100, nullable=True, description="组件")
    rank: int = Field(default=1, description="排序")
    redirect: str = Field(default=None, max_length=100, nullable=True, description="重定向")
    icon: str = Field(default=None, max_length=100, nullable=True, description="菜单图标")
    extraIcon: str = Field(default=None, max_length=100, nullable=True, description="右侧图标")
    transitionName: str = Field(default=None, max_length=100, nullable=True, description="当前页面动画")
    enterTransition: str = Field(default=None, max_length=100, nullable=True, description="进入动画")
    leaveTransition: str = Field(default=None, max_length=100, nullable=True, description="离开动画")
    dynamicLevel: int = Field(default=1, description="显示在标签页的最大数量")
    activePath: str = Field(default=None, max_length=100, nullable=True, description="菜单激活")
    auths: str = Field(default=None, max_length=100, nullable=True, description="权限标识")
    frameSrc: str = Field(default=None, max_length=100, nullable=True, description="iframe地址")
    frameLoading: bool = Field(default=True, description="iframe加载动画")
    keepAlive: bool = Field(default=False, description="缓存页面")
    hiddenTag: bool = Field(default=False, description="标签页")
    fixedTag: bool = Field(default=False, description="固定标签")
    showLink: bool = Field(default=True, description="显示链接")
    showParent: bool = Field(default=False, description="显示父菜单")


class MenuUpdate(MenuCreate, BaseModel):
    pass


class Menu(MenuUpdate, TimestampMixin, table=True):
    roles: list["Role"] = Relationship(back_populates="menus", link_model=RoleMenuLink)
