from __future__ import annotations

# standard library
from datetime import datetime, timezone

# third party
import jwt

# typing
from pydantic import SecretStr
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

# local
from SSD_Roster.src.oauth2 import authenticate_user, create_access_token
from SSD_Roster.src.templates import templates


router = APIRouter(
    prefix="/login",
    tags=["login"],
)


@router.get(
    "/",
    summary="Displayed page to login",
    response_class=HTMLResponse,
)
async def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post(
    "/",
    summary="Login-manager",
    response_class=RedirectResponse,
)
async def manage_login(
    request: Request,
    response: Response,
    username: Annotated[str, Form()] = "",
    password: Annotated[SecretStr, Form()] = "",
):
    user = await authenticate_user(username, password)
    if user is False:
        # raise HTTPException(status_code=400, detail="Incorrect username or password")
        response.status_code = 302
        return request.app.url_path_for("login")

    access_token = create_access_token(sub=user.user_id, scopes=user.scopes)
    exp = jwt.decode(access_token, options={"verify_signature": False}).get("exp")
    response.set_cookie(
        "token",
        access_token,
        expires=datetime.fromtimestamp(exp).replace(tzinfo=timezone.utc),
    )

    response.status_code = 302
    return request.app.url_path_for("root")
