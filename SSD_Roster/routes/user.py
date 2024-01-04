from __future__ import annotations

# fastapi
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# local
from SSD_Roster.src.models import UserID


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
    return "ToDo: a list containing every user with their respective access level"


@router.get(
    "/{user_id}/",
    summary="Displays a user",
    responses={404: {"description": "Not Found"}},
    response_class=HTMLResponse,
)
async def see_user(
    user_id: UserID,
):
    return f"User #{user_id}\n<timetable-link>"
