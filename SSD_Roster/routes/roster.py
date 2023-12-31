from __future__ import annotations

# standard library
from datetime import datetime

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Security
from fastapi.responses import HTMLResponse, RedirectResponse, Response

# local
from SSD_Roster.src.models import Scope, UserSchema, Week, Year
from SSD_Roster.src.oauth2 import get_current_user


router = APIRouter(
    prefix="/roster",
    tags=["roster"],
)


@router.get(
    "/",
    summary="Redirects to the current roster",
    response_class=RedirectResponse,
)
async def roster():
    date = datetime.utcnow()
    year = date.year
    week = date.isocalendar()[1]
    return router.url_path_for("see_roster", year=year, week=week)


@router.get(
    "/pdf",
    summary="Redirects to the download of the current roster",
    response_class=RedirectResponse,
)
async def roster_pdf():
    date = datetime.utcnow()
    year = date.year
    week = date.isocalendar()[1]
    return router.url_path_for("download_roster", year=year, week=week)


@router.get(
    "/{year}/{week}/",
    summary="Displays the official roster",
    responses={404: {"description": "Not Found"}},
    response_class=HTMLResponse,
)
async def see_roster(
    year: Year,
    week: Week,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_ROSTER])],
):
    return f"roster from week {week} from {year}"


@router.get(
    "/{year}/{week}/pdf",
    summary="Downloads the official roster as PDF",
    responses={
        200: {"description": "Successful Response", "content": "application/pdf"},
        404: {"description": "Not Found"},
    },
    response_class=Response,
)
async def download_roster(
    year: Year,
    week: Week,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.DOWNLOAD_ROSTER])],
):
    return Response(
        b"",
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="SSD-roster-{year}-{week}.pdf"'},
    )
