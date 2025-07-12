from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import BaseModel, TimestampMixin
from .enums import MethodType
from .link import RoleApiLink

if TYPE_CHECKING:
    from app.models import Role


class Api(BaseModel, TimestampMixin, table=True):
    path: str = Field(max_length=100, description="API路径")
    method: MethodType = Field("GET", description="请求方法")
    summary: str = Field(max_length=500, description="请求简介")
    tags: str = Field(max_length=100, description="API标签")

    roles: list["Role"] = Relationship(back_populates="apis", link_model=RoleApiLink)


class ApiCreate:
    pass

class ApiUpdate:
    pass
