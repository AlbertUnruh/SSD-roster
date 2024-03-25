from __future__ import annotations

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Depends, Request, Security
from fastapi.responses import HTMLResponse, ORJSONResponse, RedirectResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.models import (
    MessageSchema,
    MessagesResponseSchema,
    MinimalUserSchema,
    ResponseSchema,
    Scope,
    UserID,
    UserModel,
    UserResponseSchema,
    UserSchema,
    UsersResponseSchema,
)
from SSD_Roster.src.oauth2 import get_current_user
from SSD_Roster.src.utils import calculate_age


router = APIRouter(
    prefix="/users",
    tags=["user"],
)


@router.get(
    "/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def users(
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_USERS])],
):
    # ToDo: make a nice page with data
    data = await users_api(response, user)
    response.status_code = data.code
    return __import__("orjson").dumps(data.model_dump(mode="json"))


@router.get(
    "/.api",
    summary="Get details about all users",
    responses={
        200: {"model": UsersResponseSchema, "description": "Details of the requested user"},
    },
    response_class=ORJSONResponse,
)
async def users_api(
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_USERS])],
) -> UsersResponseSchema | ResponseSchema:
    all_users: list[MinimalUserSchema] = []
    for db_user in await database.fetch_all(UserModel.select()):
        all_users.append(
            MinimalUserSchema(
                user_id=db_user.user_id,
                email=db_user.email,
                displayed_name=db_user.displayed_name,
                age=calculate_age(db_user.birthday),
                scopes=db_user.scopes,
            )
        )

    count = len(all_users)

    response.status_code = 200
    return UsersResponseSchema(
        message=f"Bulk information about {count} user{'s'*(count!=1)}",
        code=200,
        count=count,
        users=all_users,
    )


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
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Depends(get_current_user)],
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
    "/{user_id}/.api",
    summary="Get details about the requested user",
    responses={
        200: {"model": UserResponseSchema, "description": "Details of the requested user"},
        404: {"model": ResponseSchema, "description": "User not found!"},
    },
    response_class=ORJSONResponse,
)
async def see_user_api(
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_USERS])],
    user_id: UserID,
) -> UserResponseSchema | ResponseSchema:
    if (requested_user := await database.fetch_one(UserModel.select().where(UserModel.user_id == user_id))) is None:
        response.status_code = 404
        return ResponseSchema(
            message=f"Unable to find user with ID {user_id}",
            code=404,
        )

    birthday = requested_user.birthday

    response.status_code = 200
    return UserResponseSchema(
        message=f"Here some information about {(name:=requested_user.displayed_name)}",
        code=200,
        user=UserModel.to_schema(requested_user),
        user_id=user_id,
        email=requested_user.email,
        displayed_name=name,
        birthday=birthday,
        age=calculate_age(birthday),
        timetable=request.app.url_path_for("see_users_timetable", user_id=user_id),
        scopes=requested_user.scopes,
    )


@router.get(
    "/{user_id}/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def see_user(
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_USERS])],
    user_id: UserID,
):
    # ToDo: make a nice page with data
    data = await see_user_api(request, response, user, user_id)
    response.status_code = data.code
    return __import__("orjson").dumps(data.model_dump(mode="json"))
