from fastapi import APIRouter
from .setting import paySetRouter
from .test import payTestRouter

payRouter = APIRouter()
payRouter.include_router(paySetRouter, prefix="/settings", tags=["支付设置"])
payRouter.include_router(payTestRouter, prefix="/test", tags=["支付测试"])
