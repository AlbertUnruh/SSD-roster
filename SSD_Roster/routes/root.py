from __future__ import annotations

# fastapi
from fastapi import APIRouter, FastAPI, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse, RedirectResponse

# local
from SSD_Roster.src.templates import templates


router = APIRouter()


@router.get(
    "/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def root(request: Request):
    # return "[CURRENT ROSTER]\n[LOGIN]"
    return templates.TemplateResponse(request, "base.html")  # ToDo: remove this line as it's just for testing


def setup(app: FastAPI):
    """Function to out-source this code from app.py to here"""

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
            redoc_favicon_url=app.url_path_for("favicon"),
        )
