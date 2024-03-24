from __future__ import annotations

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Depends, Request, Security
from fastapi.responses import HTMLResponse, ORJSONResponse, RedirectResponse, Response

# local
from SSD_Roster.src.models import MessageSchema, MessagesResponseSchema, ResponseSchema, Scope, UserID, UserSchema
from SSD_Roster.src.oauth2 import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["user"],
)


@router.get(
    "/",
    # ToDo: make a .api-variant (on hold until this function has a proper implementation)
    # summary="Returns a list of all users with their access level",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def users():
    # ToDo: a list containing every user with their respective access level
    return "ToDo: a list containing every user with their respective access level"


@router.get(
    "/me/",
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def current_user(
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Depends(get_current_user)],
):
    return (await current_user_api(request, response, user)).redirect


@router.get(
    "/me/.api",
    summary="Redirects to the current user",
    responses={
        200: {"model": ResponseSchema, "description": "Redirect available"},
        401: {"model": ResponseSchema, "description": "Not logged in!"},
    },
    response_class=ORJSONResponse,
)
async def current_user_api(
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Depends(get_current_user)],
) -> ResponseSchema:
    if user is None:
        response.status_code = 401
        return ResponseSchema(
            message="Try again after you are logged in!",
            code=401,
            redirect=request.app.url_path_for("login"),
        )
    else:
        response.status_code = 200
        return ResponseSchema(
            message="Redirect available!",
            code=200,
            redirect=request.app.url_path_for("see_user", user_id=user.user_id),
        )


@router.get(
    "/me/messages.api",
    summary="Get messages for the current user",
    responses={
        200: {"model": MessagesResponseSchema, "description": "List of all messages"},
        401: {"model": ResponseSchema, "description": "Not logged in!"},
    },
    response_class=ORJSONResponse,
)
async def get_messages_api(
    request: Request, response: Response, user: Annotated[UserSchema | None, Depends(get_current_user)]
) -> MessagesResponseSchema | ResponseSchema:
    if user is None:
        response.status_code = 401
        return ResponseSchema(
            message="Try again after you are logged in!",
            code=401,
            redirect=request.app.url_path_for("login"),
        )

    messages: list[MessageSchema] = []  # ToDo: connect to database
    count = len(messages)
    response.status_code = 200
    return MessagesResponseSchema(
        message=f"You've got {count} message{'s'*(count!=1)}",
        code=200,
        count=count,
        messages=messages,
    )


@router.get(
    "/{user_id}/",
    # ToDo. make a .api-variant (on hold until this function has a proper implementation)
    # summary="Displays a user",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def see_user(
    user_id: UserID,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_USERS])],
):
    # ToDo: actually implement it with following information: timetable, age, access level
    return f"User #{user_id}\n<timetable-link>"
