from __future__ import annotations

# standard library
from contextlib import asynccontextmanager

# fastapi
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

# local
from SSD_Roster import __version__
from SSD_Roster.routes import login, logout, logs, register, root, roster, timetable, user, verify
from SSD_Roster.src.database import database
from SSD_Roster.src.database import setup as db_setup
from SSD_Roster.src.environment import settings
from SSD_Roster.src.exception_handlers import exception_handler, validation_exception_handler
from SSD_Roster.src.models import GroupedScope


logs.inject()  # manipulates sys.stdout and sys.stderr to get logged (redirects to behave normally)


@asynccontextmanager
async def lifespan(_):  # noqa ANN001
    try:
        await database.connect()
        await db_setup()
        await GroupedScope.sync_with_db()
        yield
    finally:
        await database.disconnect()


app = FastAPI(
    debug=(DEBUG := settings.ENVIRONMENT == "development"),
    title=settings.TITLE,
    version=__version__,
    docs_url=None,
    redoc_url=None,
    middleware=[Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY.get_secret_value())],
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
root.setup(app)


app.add_exception_handler(StarletteHTTPException, exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore

app.include_router(login.router)
app.include_router(logout.router)
app.include_router(logs.router)
app.include_router(register.router)
app.include_router(root.router)
app.include_router(roster.router)
app.include_router(timetable.router)
app.include_router(user.router)
app.include_router(verify.router)


if __name__ == "__main__":
    import uvicorn  # isort: skip

    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="debug" if DEBUG else "info",
        reload=DEBUG,
    )
