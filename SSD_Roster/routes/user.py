from __future__ import annotations

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Depends, Request, Security
from fastapi.responses import HTMLResponse, RedirectResponse

# local
from SSD_Roster.src.models import Scope, UserID, UserSchema
from SSD_Roster.src.oauth2 import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["user"],
)


@router.get(
    "/",
    # ToDo: make a .json-variant
    # summary="Returns a list of all users with their access level",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def users():
    # ToDo: a list containing every user with their respective access level
    return "ToDo: a list containing every user with their respective access level"


@router.get(
    "/me/",
    # ToDo: make a .json-variant
    # summary="Redirects to the current user",
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def current_user(
    request: Request,
    user: Annotated[UserSchema | None, Depends(get_current_user)],
):
    if user is not None:
        return request.app.url_path_for("see_user", user_id=user.user_id)
    return request.app.url_path_for("login")


@router.get(
    "/{user_id}/",
    # ToDo. make a .json-variant
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
