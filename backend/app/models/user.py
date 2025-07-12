import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .base import BaseModel, TimestampMixin, Image
from .link import UserRoleLink
from .department import Department


if TYPE_CHECKING:
    from . import Role


class UserBase(BaseModel):
    username: str = Field(max_length=20, unique=True, description="用户名称")
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    password: str = Field(min_length=8, max_length=256, description="密码")
    status: int = Field(default=1, index=True, description="是否激活")
    is_superuser: bool = Field(default=False, description="是否为超级管理员")


class User(UserBase, TimestampMixin, table=True):
    nickname: str = Field(default=None, max_length=30, nullable=True, description="用户昵称")
    avatar: str = Field(default=None, max_length=255, nullable=True, description="头像文件名称")
    sex: int = Field(default=1, description="性别, 0: 女, 1: 男")
    phone: str = Field(default=None, max_length=20, nullable=True, unique=True, description="电话")
    last_login: datetime = Field(default=None, nullable=True, description="最后登录时间")
    remark: str = Field(default=None, max_length=500, nullable=True, description="备注")

    department_id: uuid.UUID | None = Field(default=None, index=True, foreign_key="department.id")
    department: Department | None = Relationship(back_populates="users")

    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)


class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: str = Field(max_length=20, unique=True, description="用户名称")
    nickname: str = Field(default=None, max_length=30, nullable=True, description="用户昵称")
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    sex: int = Field(default=1, description="性别, 0: 女, 1: 男")
    phone: str = Field(default=None, max_length=20, nullable=True, unique=True, description="电话")

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

class UserFiter(BaseModel):
    username: str | None
    email: str | None
    departId: str | None

class UserResetPwd(BaseModel):
    newPwd: str

class UserAvatar(BaseModel):
    avatar: Image

class UpdateStatus(BaseModel):
    status: int

class UpdateUserRoles(BaseModel):
    roleIds: list[str]
