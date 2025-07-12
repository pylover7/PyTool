from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4


from sqlmodel import Field, SQLModel
from fastapi.responses import JSONResponse

from app.settings import settings


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    async def to_dict(self, exclude_fields: list[str] | None = None):
        if exclude_fields is None:
            exclude_fields = []

        d = {}
        for field in self.model_fields:
            if field not in exclude_fields:
                value = getattr(self, field)
                if isinstance(value, datetime):
                    value = value.strftime(settings.DATETIME_FORMAT)
                if isinstance(value, UUID):
                    value = str(value)
                d[field] = value
        return d


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class Success(JSONResponse):
    def __init__(
        self,
        code: int = 200,
        msg: Optional[str] = "OK",
        data: Optional[Any] = None,
        **kwargs,
    ):
        content = {"code": code, "msg": msg, "data": data}
        content.update(kwargs)
        super().__init__(content=content, status_code=code)


class Fail(JSONResponse):
    def __init__(
        self,
        code: int = 400,
        msg: Optional[str] = "Fail",
        data: Optional[Any] = None,
        **kwargs,
    ):
        content = {"code": code, "msg": msg, "data": data}
        content.update(kwargs)
        super().__init__(content=content, status_code=code)


class SuccessExtra(JSONResponse):
    def __init__(
        self,
        code: int = 200,
        msg: Optional[str] = "OK",
        data: Optional[Any] = None,
        total: int = 0,
        currentPage: int = 1,
        pageSize: int = 20,
        **kwargs,
    ):
        content = {
            "code": code,
            "msg": msg,
            "data": data,
            "total": total,
            "currentPage": currentPage,
            "pageSize": pageSize,
        }
        content.update(kwargs)
        super().__init__(content=content, status_code=code)


class FailAuth(JSONResponse):
    def __init__(
            self,
            code: int = 401,
            msg: Optional[str] = "Unauthorized",
            **kwargs,
    ):
        content = {"code": code, "msg": msg}
        content.update(kwargs)
        super().__init__(content=content, status_code=code)


class Image(SQLModel):
    base64: str

    class Meta:
        extra = "allow"
