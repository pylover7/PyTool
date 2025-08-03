from fastapi import APIRouter

from app.core.dependency import DependPermission

from .base import base_router
from .system import systemRouter
from .pay import payRouter

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(
    systemRouter,
    prefix="/system",
    dependencies=[DependPermission])
