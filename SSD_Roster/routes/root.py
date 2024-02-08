from __future__ import annotations

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

# local
from SSD_Roster.src.messages import flash
from SSD_Roster.src.models import MessageCategory
from SSD_Roster.src.oauth2 import authenticate_user, create_access_token
from SSD_Roster.src.templates import templates


router = APIRouter()


@router.get(
    "/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def root(request: Request):
    for category in MessageCategory:  # type: ignore  # ToDo: remove in demo messages
        flash(request, f"A demo message with category {category}", category)
    return templates.TemplateResponse(request, "root.html")


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

    @app.post("/token")
    async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        user = await authenticate_user(form_data.username, form_data.password)
        if user is False:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        access_token = create_access_token(sub=user.user_id, scopes=form_data.scopes)

        return {"access_token": access_token, "token_type": "bearer"}
