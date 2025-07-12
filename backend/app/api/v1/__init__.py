from fastapi import APIRouter

from app.core.dependency import DependPermission

from .base import base_router
from .system import systemRouter
from .goods import goodsRouter
from .card import cardRouter
from .order import orderRouter
from .pay import payRouter

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(systemRouter, prefix="/system", dependencies=[DependPermission])
v1_router.include_router(goodsRouter, prefix="/goods", dependencies=[DependPermission])
v1_router.include_router(cardRouter, prefix="/card", dependencies=[DependPermission])
v1_router.include_router(orderRouter, prefix="/order", dependencies=[DependPermission])
v1_router.include_router(payRouter, prefix="/pay", dependencies=[DependPermission])



