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
    summary="Returns a list of all users with their access level",
    response_class=HTMLResponse,
)
async def users():
    # ToDo: a list containing every user with their respective access level
    return "ToDo: a list containing every user with their respective access level"


@router.get(
    "/me/",
    summary="Redirects to the current user",
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
    summary="Displays a user",
    responses={404: {"description": "Not Found"}},
    response_class=HTMLResponse,
)
async def see_user(
    user_id: UserID,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_USERS])],
):
    # ToDo: actually implement it with following information: timetable, age, access level
    return f"User #{user_id}\n<timetable-link>"
