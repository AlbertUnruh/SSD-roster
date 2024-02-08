from __future__ import annotations

# typing
from pydantic import EmailStr, PastDate
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.email import send_verification_email
from SSD_Roster.src.messages import flash
from SSD_Roster.src.models import MessageCategory, UserModel, VerificationCodesModel
from SSD_Roster.src.templates import templates
from SSD_Roster.src.verification import generate_code


router = APIRouter(
    prefix="/register",
    tags=["register"],
)


@router.get(
    "/",
    summary="Displayed page to register",
    response_class=HTMLResponse,
)
async def register(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.post(
    "/",
    summary="Registration-manager",
    response_class=RedirectResponse,
)
async def manage_registration(
    request: Request,
    response: Response,
    username: Annotated[str, Form()] = None,
    email: Annotated[EmailStr, Form()] = None,
    birthday: Annotated[PastDate, Form()] = None,
):
    # everything set?
    if any((username is None, email is None, birthday is None)):
        response.status_code = 302
        return request.app.url_path_for("register")

    # email already used?
    if await database.fetch_one(UserModel.select().where(UserModel.email == email)) is not None:
        flash(request, f"The E-Mail {email} is already registered!", MessageCategory.ERROR)
        response.status_code = 302
        return request.app.url_path_for("register")

    # username already used?
    if await database.fetch_one(UserModel.select().where(UserModel.username == username)) is not None:
        flash(request, f"The username {username} is already registered!", MessageCategory.ERROR)
        response.status_code = 302
        return request.app.url_path_for("register")

    user_id = await database.execute(
        UserModel.insert().values(
            username=username,
            displayed_name=username,
            email=email,
            email_verified=False,
            user_verified=False,
            birthday=birthday,
            password=None,
            scopes="USER",
        )
    )
    code = generate_code()
    await database.execute(VerificationCodesModel.insert().values(user_id=user_id, email=email, code=code))

    if await send_verification_email(request, email, code):
        flash(request, f"A code has been sent to {email}. Either enter it here or use the link in the mail.")
    else:
        flash(request, f"No email has been send to {email}! Please contact an admin!", MessageCategory.DANGER)

    response.status_code = 302
    return request.app.url_path_for("verify") + f"?email={email}"


# ToDo: maybe endpoint for admins to create users (which are user-verified immediately, just email-verification missing
#       (also to let the user set a password))
