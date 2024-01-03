# standard library
from contextlib import asynccontextmanager

# fastapi
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

# local
from SSD_Roster import __version__
from SSD_Roster.routes import login, register, root, roster, timetable, user
from SSD_Roster.src.database import database
from SSD_Roster.src.database import setup as db_setup
from SSD_Roster.src.environment import settings
from SSD_Roster.src.exception_handlers import exception_handler, validation_exception_handler


@asynccontextmanager
async def lifespan(_):  # noqa ANN001
    try:
        await database.connect()
        await db_setup()
        yield
    finally:
        await database.disconnect()


app = FastAPI(
    debug=(DEBUG := settings.ENVIRONMENT == "development"),
    title=settings.TITLE,
    version=__version__,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
root.setup(app)


app.add_exception_handler(StarletteHTTPException, exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore

app.include_router(login.router)
app.include_router(register.router)
app.include_router(root.router)
app.include_router(roster.router)
app.include_router(timetable.router)
app.include_router(user.router)


if __name__ == "__main__":
    import uvicorn  # isort: skip

    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="debug" if DEBUG else "info",
        reload=DEBUG,
    )
