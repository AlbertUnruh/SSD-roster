from __future__ import annotations

# standard library
from datetime import datetime, timedelta

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form, Request, Security
from fastapi.responses import HTMLResponse, RedirectResponse, Response

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
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def overview():
    # ToDo: create roster, function to search for other timetables
    return "ToDo: create roster, function to search for other timetables"


@router.get(
    "/edit",
    # ToDo: make a .json-variant (somehow)
    # summary="Edit personal timetable",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def edit_timetable(
    request: Request,
    user: Annotated[UserSchema, Security(get_current_user, scopes=[Scope.MANAGE_OWN_CALENDAR])],
    page: PageID = 0,
):
    date = datetime.utcnow() + timedelta(weeks=page)
    year = date.year
    week = date.isocalendar().week

    # navigation
    url = request.app.url_path_for("edit_timetable")
    before = f"{url}?page={max(page - 1, 0)}"
    current = f"{url}?page=0"
    after = f"{url}?page={page + 1}"
    db_timetable: TimetableModel | None = await database.fetch_one(
        TimetableModel.select().where(
            TimetableModel.user_id == user.user_id, TimetableModel.year == year, TimetableModel.week == week
        )
    )
    if db_timetable is None:
        matrix = Timetable.model_fields["availability_matrix"].get_default()
    else:
        timetable_ = Timetable(**TimetableModel.to_schema(db_timetable).model_dump())
        matrix = timetable_.availability_matrix

    owner = await database.fetch_one(UserModel.select().where(UserModel.user_id == user.user_id))

    return templates.TemplateResponse(
        request,
        "timetable-edit.html",
        {
            "week": week,
            "year": year,
            "user": owner,
            "page": page,
            "before": before,
            "current": current,
            "after": after,
            "matrix": matrix,
        },
        200 if db_timetable is not None else 404,  # or like this ^^: 200+(db_timetable is None)*204
    )


@router.post(
    "/submit",
    # ToDo: make a .json-variant
    # summary="Submit edits",
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def submit_timetable(
    request: Request,
    response: Response,
    user: Annotated[UserSchema, Security(get_current_user, scopes=[Scope.MANAGE_OWN_CALENDAR])],
    page: Annotated[PageID, Form()] = 0,
):
    date = datetime.utcnow() + timedelta(weeks=page)
    year = date.year
    week = date.isocalendar().week

    timetable = Timetable(user_id=user.user_id, date_anchor=(year, week))
    timetable.availability_matrix = Timetable.matrix_from_form(
        list(filter(lambda t: len(t[0]) == 2 and t[0].isnumeric(), (await request.form()).items()))
    )

    # ToDo: update database
    # await database.execute(timetable.to_model().insert())  /!\

    response.status_code = 302
    return request.app.url_path_for("edit_timetable")


@router.get(
    "/{user_id}",
    # ToDo: make a .json-variant
    # summary="Displays the timetable of an user",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def see_users_timetable(
    request: Request,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_OTHERS_CALENDAR])],
    user_id: UserID,
    page: PageID = 0,
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
