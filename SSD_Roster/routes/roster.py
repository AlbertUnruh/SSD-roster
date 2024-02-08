from __future__ import annotations

# standard library
from datetime import datetime

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Request, Security
from fastapi.responses import HTMLResponse, RedirectResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.models import GroupedScope, RosterModel, Scope, UserModel, UserSchema, Week, Year
from SSD_Roster.src.oauth2 import get_current_user
from SSD_Roster.src.roster import Roster
from SSD_Roster.src.templates import templates


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
    iso = datetime.utcnow().isocalendar()
    return router.url_path_for("download_roster", year=iso.year, week=iso.week)


@router.get(
    "/{year}/{week}/",
    summary="Displays the official roster",
    responses={404: {"description": "Not Found"}},
    response_class=HTMLResponse,
)
async def see_roster(
    request: Request,
    response: Response,
    year: Year,
    week: Week,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_ROSTER])],
):
    # ToDo: @HTML: add navigation (week before | current week | week after)*
    #              *with before/after being relative to displayed week
    db_roster: RosterModel | None = await database.fetch_one(
        RosterModel.select().where(RosterModel.year == year, RosterModel.week == week)
    )
    if db_roster is None:
        user_matrix = Roster.model_fields["user_matrix"].get_default()
        published_by = None
        published_at = None
    else:
        roster_ = Roster(**RosterModel.to_schema(db_roster).model_dump())
        user_matrix = roster_.user_matrix
        published_by = roster_.published_by
        published_at = roster_.published_at

    matrix = []
    _cache: dict[int | None, str] = {
        published_by: await database.fetch_one(UserModel.select().where(UserModel.user_id == published_by))
        or f"User #{published_by}",
        None: "",
    }
    for day in user_matrix:
        matrix.append([])
        for shift in day:
            matrix[-1].append([])
            for _user in shift:
                if (_u := _cache.get(_user)) is None:
                    if (
                        _u := await database.fetch_one(UserModel.select().where(UserModel.user_id == _user))
                    ) is not None:
                        _cache[_user] = _u.displayed_name
                    else:
                        _cache[_user] = _u = f"User #{_user}"
                matrix[-1][-1].append(_u)

    return templates.TemplateResponse(
        request,
        "roster.html",
        {
            "week": week,
            "year": year,
            "published": published_at,
            "user": published_by,
            "user_url": request.app.url_path_for("user", user_id=published_by) if published_by else "#",
            "public_download": Scope.DOWNLOAD_ROSTER.value in GroupedScope.PUBLIC,
            "matrix": matrix,
        },
        200 if db_roster is not None else 404,  # or like this ^^: 200+(db_roster is None)*204
    )


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
    # ToDo: actually implement downloading the roster as a PDF
    return Response(
        b"",
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="SSD-roster-{year}-{week}.pdf"'},
    )


# ToDo: endpoint to create roster
# ToDo: endpoint to view own (created by one self) rosters
# ToDo: endpoint to submit an own roster
# ToDo: endpoint to approve a roster
