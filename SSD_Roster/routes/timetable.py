from fastapi import APIRouter

from SSD_Roster.src.models import UserID, PageID


router = APIRouter(
    prefix="/timetable",
    tags=["timetable"],
)


@router.get(
    "/",
    summary="Gives an overview what can be done here",
)
async def overview():
    return "ToDo: create roster, function to search for other timetables"


@router.get(
    "/{user_id}",
    summary="Displays the timetable of an user",
    responses={404: {"description": "Not Found"}},
)
async def see_user(
    user_id: UserID,
    page: PageID = 0,
):
    return f"timetable #{page} of user #{user_id}"
