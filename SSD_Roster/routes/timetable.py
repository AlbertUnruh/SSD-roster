# fastapi
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# local
from SSD_Roster.src.models import PageID, UserID


router = APIRouter(
    prefix="/timetable",
    tags=["timetable"],
)


@router.get(
    "/",
    summary="Gives an overview what can be done here",
    response_class=HTMLResponse,
)
async def overview():
    return "ToDo: create roster, function to search for other timetables"


@router.get(
    "/{user_id}",
    summary="Displays the timetable of an user",
    responses={404: {"description": "Not Found"}},
    response_class=HTMLResponse,
)
async def see_user(
    user_id: UserID,
    page: PageID = 0,
):
    return f"timetable #{page} of user #{user_id}"
