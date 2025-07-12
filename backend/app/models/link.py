from uuid import UUID

from sqlmodel import SQLModel, Field


class UserRoleLink(SQLModel, table=True):
    user_id: UUID | None = Field(default=None, foreign_key="user.id", primary_key=True, description="用户id")
    role_id: UUID | None = Field(default=None, foreign_key="role.id", primary_key=True, description="角色id")


class RoleMenuLink(SQLModel, table=True):
    role_id: UUID | None = Field(default=None, foreign_key="role.id", primary_key=True, description="角色id")
    menu_id: UUID | None = Field(default=None, foreign_key="menu.id", primary_key=True, description="菜单id")


class RoleApiLink(SQLModel, table=True):
    role_id: UUID | None = Field(default=None, foreign_key="role.id", primary_key=True, description="角色id")
    api_id: UUID | None = Field(default=None, foreign_key="api.id", primary_key=True, description="接口id")
