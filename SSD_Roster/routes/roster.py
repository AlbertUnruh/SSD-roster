from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from datetime import datetime

from SSD_Roster.src.models import Year, Week


router = APIRouter(
    prefix="/roster",
    tags=["roster"],
)


@router.get(
    "/",
    summary="Redirects to the current roster",
)
async def roster():
    date = datetime.utcnow()
    year = date.year
    week = date.isocalendar()[1]
    return RedirectResponse(router.url_path_for("see_roster", year=year, week=week))


@router.get(
    "/{year}/{week}/",
    summary="Displays the official roster",
    responses={404: {"description": "Not Found"}},
)
async def see_roster(
    year: Year,
    week: Week,
):
    return f"roster from week {week} from {year}"
