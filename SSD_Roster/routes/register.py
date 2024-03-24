from __future__ import annotations

# typing
from pydantic import EmailStr, PastDate
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, ORJSONResponse, RedirectResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.email import send_verification_email
from SSD_Roster.src.messages import flash
from SSD_Roster.src.models import MessageCategory, ResponseSchema, UserModel, VerificationCodesModel
from SSD_Roster.src.templates import templates
from SSD_Roster.src.verification import generate_code


router = APIRouter(
    prefix="/register",
    tags=["login"],
)


@router.get(
    "/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def register(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.post(
    "/",
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def manage_registration(
    request: Request,
    response: Response,
    username: Annotated[str, Form()] = None,
    email: Annotated[EmailStr, Form()] = None,
    birthday: Annotated[PastDate, Form()] = None,
):
    data: ResponseSchema = await register_api(request, response, username, email, birthday)

    response.status_code = 302

    match data.code:
        case 201:
            flash(request, data.message)
            return data.redirect
        case 400:
            pass  # the user may figure it out themselves that something is missing
        case 403:
            flash(request, data.message, MessageCategory.ERROR)
        case 500:
            flash(request, data.message, MessageCategory.DANGER)

    return request.app.url_path_for("register")


@router.post(
    "/.api",
    summary="Endpoint to register a new user",
    response_class=ORJSONResponse,
    responses={
        201: {"model": ResponseSchema, "description": "Everything worked; a redirect is included"},
        400: {"model": ResponseSchema, "description": "Some form-fields are missing or not well formatted"},
        403: {"model": ResponseSchema, "description": "Already registered (E-Mail/username)"},
        500: {"model": ResponseSchema, "description": "E-Mail could not be sent (or any other error...)"},
    },
)
async def register_api(
    request: Request,
    response: Response,
    username: Annotated[str, Form()] = None,
    email: Annotated[EmailStr, Form()] = None,
    birthday: Annotated[PastDate, Form()] = None,
) -> ResponseSchema:
    # everything set?
    if (
        missing := (["username"] if username is None else [])
        + (["email"] if email is None else [])
        + (["birthday"] if birthday is None else [])
    ):
        response.status_code = 400
        return ResponseSchema(message="Following form-fields need to be set: " + ", ".join(missing), code=400)

    # email already used?
    if await database.fetch_one(UserModel.select().where(UserModel.email == email)) is not None:
        response.status_code = 403
        return ResponseSchema(message=f"The E-Mail {email} is already registered!", code=403)

    # username already used?
    if await database.fetch_one(UserModel.select().where(UserModel.username == username)) is not None:
        response.status_code = 403
        return ResponseSchema(message=f"The username {username} is already registered!", code=403)

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
        response.status_code = 201
        return ResponseSchema(
            message=f"A code has been sent to {email}."
            + (" Either enter it here or use the link in the mail." * (not request.url.path.endswith(".api"))),
            code=201,
            redirect=request.app.url_path_for("verify") + f"?email={email}",
        )
    else:
        response.status_code = 500
        return ResponseSchema(message=f"No email has been send to {email}! Please contact an admin!", code=500)


# ToDo: maybe endpoint for admins to create users (which are user-verified immediately, just email-verification missing
#       (also to let the user set a password))
