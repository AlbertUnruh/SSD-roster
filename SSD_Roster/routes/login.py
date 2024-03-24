from __future__ import annotations

# standard library
from datetime import datetime, timezone

# third party
import jwt

# typing
from pydantic import SecretStr
from typing import Annotated, Literal

# fastapi
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, ORJSONResponse, RedirectResponse, Response

# local
from SSD_Roster.routes.user import get_messages_api
from SSD_Roster.src.database import database
from SSD_Roster.src.messages import flash
from SSD_Roster.src.models import LoginResponseSchema, MessageCategory, ResponseSchema, UserModel, UserSchema
from SSD_Roster.src.oauth2 import authenticate_user, create_access_token
from SSD_Roster.src.templates import templates


router = APIRouter(
    prefix="/login",
    tags=["login"],
)


@router.get(
    "/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post(
    "/",
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def manage_login(
    request: Request,
    response: Response,
    username: Annotated[str, Form()] = "",
    password: Annotated[SecretStr, Form()] = "",
):
    data: LoginResponseSchema | ResponseSchema = await manage_login_api(response, username, password)

    if not isinstance(data, LoginResponseSchema):  # unsuccessful
        flash(request, data.message, MessageCategory.ERROR)
        response.status_code = 302
        return request.app.url_path_for("login")

    flash(request, data.message, MessageCategory.SUCCESS)

    for message in (await get_messages_api(request, response, data.user)).messages:
        flash(request, message.content, message.category)

    response.set_cookie(
        "token",
        data.token,
        expires=data.expiration,
        httponly=True,
    )
    response.status_code = 302
    return request.app.url_path_for("root")


@router.post(
    "/.api",
    summary="Endpoint for login",
    responses={
        200: {"model": LoginResponseSchema, "description": "Login successful"},
        401: {"model": ResponseSchema, "description": "Unable to log in"},
    },
    response_class=ORJSONResponse,
)
async def manage_login_api(
    response: Response,
    username: Annotated[str, Form()] = "",
    password: Annotated[SecretStr, Form()] = "",
) -> LoginResponseSchema | ResponseSchema:
    user: UserSchema | Literal[False] = await authenticate_user(username, password)

    # can't log in
    if user is False:
        response.status_code = 401
        # add a bit of context for freshly registered users
        if (_user := await database.fetch_one(UserModel.select().where(UserModel.username == username))) is not None:
            _message_fractals: list[str] = []
            if _user.email_verified is False:
                _message_fractals.append("without your email being verified")
            if _user.user_verified is False:
                _message_fractals.append("without being verified by an admin")
            return ResponseSchema(message="You can't login " + " or ".join(_message_fractals) + "!", code=401)
        else:
            # just bad credentials...
            return ResponseSchema(message="Incorrect username or password!", code=401)

    # get appropriate greeting
    if user.birthday.month == datetime.now().month and user.birthday.day == datetime.now().day:
        greeting = f"Happy Birthday {user.displayed_name}! You've successfully logged in"
    else:
        greeting = f"Hello {user.displayed_name}, your login was successful"

    # actually create token for access
    access_token = create_access_token(sub=user.user_id, scopes=user.scopes)
    exp = jwt.decode(access_token, options={"verify_signature": False}).get("exp")

    response.status_code = 200
    return LoginResponseSchema(
        message=greeting,
        code=200,
        user=user,  # only internally used
        user_id=user.user_id,
        token=access_token,
        expiration=datetime.fromtimestamp(exp).replace(tzinfo=timezone.utc),
    )
