from pathlib import Path

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.core.database import init_data
from app.core.exceptions import SettingNotFound
from app.core.init import make_middlewares, register_routers, register_exceptions

try:
    from app.settings import settings
except ImportError:
    raise SettingNotFound("无法加载配置文件，请检查配置文件是否存在！！！")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
    )
    register_exceptions(app)
    register_routers(app, prefix="/api")
    static_path = Path.joinpath(Path(__file__).parent, "static")
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    return app


app = create_app()


@app.on_event("startup")
async def startup_event():
    await init_data(app)