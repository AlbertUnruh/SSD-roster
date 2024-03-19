from __future__ import annotations

# standard library
from datetime import datetime, timedelta

# typing
import annotated_types
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form, Request, Security
from fastapi.responses import HTMLResponse, ORJSONResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.models import PageID, Scope, TimetableModel, UserID, UserModel, UserSchema
from SSD_Roster.src.oauth2 import get_current_user
from SSD_Roster.src.templates import templates
from SSD_Roster.src.timetable import Timetable


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
    # ToDo: create roster, function to search for other timetables
    return "ToDo: create roster, function to search for other timetables"


@router.get(
    "/{user_id}",
    summary="Displays the timetable of an user",
    responses={404: {"description": "Not Found"}},
    response_class=HTMLResponse,
)
async def see_users_timetable(
    request: Request,
    user_id: UserID,
    page: PageID = 0,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_OTHERS_CALENDAR])] = None,
):
    date = datetime.utcnow() + timedelta(weeks=page)
    year = date.year
    week = date.isocalendar().week

    # navigation
    url = request.app.url_path_for("see_users_timetable", user_id=user_id)
    before = f"{url}?page={max(page - 1, 0)}"
    current = f"{url}?page=0"
    after = f"{url}?page={page + 1}"

    db_timetable: TimetableModel | None = await database.fetch_one(
        TimetableModel.select().where(
            TimetableModel.user_id == user_id, TimetableModel.year == year, TimetableModel.week == week
        )
    )
    if db_timetable is None:
        matrix = Timetable.model_fields["availability_matrix"].get_default()
    else:
        timetable_ = Timetable(**TimetableModel.to_schema(db_timetable).model_dump())
        matrix = timetable_.availability_matrix

    owner = await database.fetch_one(UserModel.select().where(UserModel.user_id == user_id))

    return templates.TemplateResponse(
        request,
        "timetable.html",
        {
            "week": week,
            "year": year,
            "user": owner,
            "before": before,
            "current": current,
            "after": after,
            "matrix": matrix,
        },
        200 if db_timetable is not None else 404,  # or like this ^^: 200+(db_timetable is None)*204
    )


@router.get(
    "/edit",
    summary="Edit personal timetable",
    response_class=HTMLResponse,
)
async def edit(
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.MANAGE_OWN_CALENDAR])],
    page: PageID,
):
    # date = datetime.utcnow() + timedelta(weeks=page)
    # year = date.year
    # week = date.isocalendar().week
    pass  # ToDo: display HTML (with radiobuttons for selection?)


@router.post(
    "/submit",
    summary="Submit edits",
    response_class=ORJSONResponse,
)
async def submit(
    request: Request,
    response: Response,
    user: Annotated[UserSchema, Security(get_current_user, scopes=[Scope.MANAGE_OWN_CALENDAR])],
    page: Annotated[PageID, Form()],
    matrix_str1d: Annotated[str, annotated_types.MinLen(20), annotated_types.MaxLen(20), Form()],
):
    date = datetime.utcnow() + timedelta(weeks=page)
    year = date.year
    week = date.isocalendar().week

    timetable = Timetable()
    timetable.availability_matrix = Timetable.matrix_from_str1d(matrix_str1d)
    timetable.user_id = user.user_id
    timetable.date_anchor = (year, week)
    pass  # ToDo: logic to update database (should be straight forward)
