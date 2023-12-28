from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from SSD_Roster import __version__
from SSD_Roster.routes import login, register, root, roster, timetable, user
from SSD_Roster.src.environment import SETTINGS


app = FastAPI(
    debug=(DEBUG := SETTINGS.ENVIRONMENT == "development"),
    title=SETTINGS.TITLE,
    version=__version__,
    docs_url=None,
    redoc_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse("/static/favicon/favicon.ico")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url=app.url_path_for("favicon"),
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url=app.url_path_for("favicon")
    )


app.include_router(login.router)
app.include_router(register.router)
app.include_router(root.router)
app.include_router(roster.router)
app.include_router(timetable.router)
app.include_router(user.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=SETTINGS.HOST,
        port=SETTINGS.PORT,
        log_level="info",
        reload=DEBUG,
    )
