from fastapi import APIRouter

from app.models import Success
from app.utils.emails import send_email

payTestRouter = APIRouter()


@payTestRouter.get("/email", summary="测试邮件发送")
async def email_test(email: str):
    if send_email(email, "测试邮件", "这是一封测试邮件"):
        return Success(msg="发送成功")
    return Success(code=201, msg="发送失败")
