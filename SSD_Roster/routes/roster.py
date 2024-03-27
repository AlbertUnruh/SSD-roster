from __future__ import annotations

# standard library
import asyncio
from datetime import datetime

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Request, Security
from fastapi.responses import HTMLResponse, ORJSONResponse, RedirectResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.models import (
    GroupedScope,
    ResponseSchema,
    RosterModel,
    RosterResponseSchema,
    RosterSchema,
    Scope,
    UserModel,
    UserSchema,
    Week,
    Year,
)
from SSD_Roster.src.oauth2 import get_current_user
from SSD_Roster.src.roster import Roster
from SSD_Roster.src.templates import templates


router = APIRouter(
    prefix="/roster",
    tags=["roster"],
)


@router.get(
    "/",
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def roster():
    return (await roster_api()).redirect.removesuffix(".api")


@router.get(
    "/pdf",
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def roster_pdf():
    return (await roster_pdf_api()).redirect


@router.get(
    "/.api",
    summary="Get url for current roster",
    response_class=ORJSONResponse,
)
async def roster_api() -> ResponseSchema:
    iso = datetime.utcnow().isocalendar()
    return ResponseSchema(
        message="The url for the current roster",
        code=200,
        redirect=router.url_path_for("see_roster_api", year=iso.year, week=iso.week),
    )


@router.get(
    "/pdf.api",
    summary="Get url for current roster download",
    response_class=ORJSONResponse,
)
async def roster_pdf_api() -> ResponseSchema:
    iso = datetime.utcnow().isocalendar()
    return ResponseSchema(
        message="The url for the download of the current roster",
        code=200,
        redirect=router.url_path_for("download_roster", year=iso.year, week=iso.week),
    )


@router.get(
    "/{year}/{week}/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def see_roster(
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_ROSTER])],
    year: Year,
    week: Week,
):
    # ToDo: @HTML: add navigation (week before | current week | week after)*
    #              *with before/after being relative to displayed week
    data: RosterResponseSchema = await see_roster_api(response, user, year, week)
    rstr: RosterSchema = data.roster
    matrix = []
    _cache: dict[int | None, str] = {
        rstr.published_by: await database.fetch_one(UserModel.select().where(UserModel.user_id == rstr.published_by))
        or f"User #{rstr.published_by}",
        None: "",
    }
    for day in rstr.user_matrix:
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
            "week": rstr.date_anchor[1],
            "year": rstr.date_anchor[0],
            "published": rstr.published_at,
            "user": rstr.published_by,
            "user_url": request.app.url_path_for("user", user_id=rstr.published_by) if rstr.published_by else "#",
            "public_download": Scope.DOWNLOAD_ROSTER.value in GroupedScope.PUBLIC,
            "matrix": matrix,
        },
        data.code,
    )


@router.get(
    "/{year}/{week}/.api",
    summary="Displays the official roster",
    responses={
        200: {"model": RosterResponseSchema, "description": "Roster available"},
        404: {"model": RosterResponseSchema, "description": "Not Found"},
    },
    response_class=ORJSONResponse,
)
async def see_roster_api(
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_ROSTER])],
    year: Year,
    week: Week,
) -> RosterResponseSchema:
    db_roster: RosterModel | None = await database.fetch_one(
        RosterModel.select().where(RosterModel.year == year, RosterModel.week == week)
    )
    if db_roster is None:
        response.status_code = 404
        return RosterResponseSchema(
            message=f"Unable to find roster for year {year} and week {week}",
            code=404,
            roster=RosterSchema(
                user_matrix=Roster.model_fields["user_matrix"].get_default(),
                date_anchor=(year, week),
                published_by=None,
                published_at=None,
            ),
        )
    else:
        roster_ = RosterModel.to_schema(db_roster)
        response.status_code = 200
        return RosterResponseSchema(
            message=f"Roster for year {year} and week {week} "
            f"(last updated: {roster_.published_at.strftime("%d/%m/%Y, %H:%M:%S")})",
            code=200,
            roster=roster_,
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
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.DOWNLOAD_ROSTER])],
    year: Year,
    week: Week,
):
    data: RosterResponseSchema = await see_roster_api(response, user, year, week)
    roster_: Roster = Roster(**data.roster.model_dump())
    return Response(
        # ToDo: depending on final implementation call another method here to get bytes
        await asyncio.to_thread(roster_.export_to_pdf),
        status_code=data.code,
        headers={"Content-Disposition": f'attachment; filename="SSD-roster-{year}-{week}.pdf"'},
        media_type="application/pdf",
    )


# ToDo: endpoint to create & submit an own roster
# ToDo: endpoint to approve a roster

# ToDo: endpoint for collaborative roster (logic for approval needed)
