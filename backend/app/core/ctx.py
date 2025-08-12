import contextvars

from starlette.background import BackgroundTasks

CTX_USER_ID: contextvars.ContextVar[str] = contextvars.ContextVar(
    "user_id", default="")
CTX_BG_TASKS: contextvars.ContextVar[BackgroundTasks] = contextvars.ContextVar(
    "bg_task", default=None)
