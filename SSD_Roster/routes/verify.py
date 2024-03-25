from __future__ import annotations

# typing
from pydantic import EmailStr, SecretStr
from typing import Annotated, Optional

# fastapi
from fastapi import APIRouter, Form, Request, Security
from fastapi.responses import HTMLResponse, ORJSONResponse, RedirectResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.messages import flash
from SSD_Roster.src.models import (
    MessageCategory,
    MinimalUserSchema,
    ResponseSchema,
    Scope,
    UserID,
    UserModel,
    UserSchema,
    UsersResponseSchema,
    VerificationCodesModel,
)
from SSD_Roster.src.oauth2 import get_current_user, get_password_hash
from SSD_Roster.src.templates import templates
from SSD_Roster.src.utils import calculate_age
from SSD_Roster.src.verification import verify_code


router = APIRouter(
    prefix="/verify",
    tags=["verify"],
)


@router.get(
    "/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def verify(
    request: Request,
    email: Optional[EmailStr] = None,
    code: Optional[str] = None,
):
    return templates.TemplateResponse(request, "verify.html", {"email": email or "", "code": code or ""})


@router.post(
    "/",
    include_in_schema=False,
    response_class=RedirectResponse,
)
async def manage_verification(
    request: Request,
    response: Response,
    email: Annotated[EmailStr, Form()] = None,
    code: Annotated[str, Form()] = None,
    password: Annotated[SecretStr, Form()] = None,
):
    data: ResponseSchema = await manage_verification_api(request, response, email, code, password)

    if data.code == 200:
        flash(request, data.message, MessageCategory.SUCCESS)
        response.status_code = 302
        return data.redirect

    flash(request, data.message, MessageCategory.ERROR)
    response.status_code = 302
    return request.app.url_path_for("verify") + f"?email={email or ''}&code={code or ''}"


@router.post(
    "/.api",
    summary="Registration-manager",
    responses={
        200: {"model": ResponseSchema, "description": "Email successfully verified"},
        401: {"model": ResponseSchema, "description": "Invalid email or code"},
    },
    response_class=ORJSONResponse,
)
async def manage_verification_api(
    request: Request,
    response: Response,
    email: Annotated[EmailStr, Form()] = None,
    code: Annotated[str, Form()] = None,
    password: Annotated[SecretStr, Form()] = None,
):
    # everything set?
    if any((email is None, code is None, password is None)):
        _message_fractals: list[str] = []
        if email is None:
            _message_fractals.append("email")
        if code is None:
            _message_fractals.append("code")
        if password is None:
            _message_fractals.append("password")
        response.status_code = 401
        return ResponseSchema(
            message="Verification not possible unless "
            + " and ".join(_message_fractals)
            + f" {'are' if len(_message_fractals)!=1 else 'is'} set!",
            code=401,
        )

    # invalid email?
    if (user := await database.fetch_one(UserModel.select().where(UserModel.email == email))) is None:
        response.status_code = 401
        return ResponseSchema(message=f"Invalid email {email}!", code=401)

    # invalid code?
    if not await verify_code(user, code):
        response.status_code = 401
        return ResponseSchema(message=f"Invalid code {code}!", code=401)

    # set password
    await database.execute(
        UserModel.update()  # type: ignore
        .where(UserModel.email == user.email)
        .values(password=get_password_hash(password), email_verified=True)
    )

    await database.execute(VerificationCodesModel.delete().where(VerificationCodesModel.user_id == user.user_id))

    is_api = ".api" in request.url.path

    response.status_code = 200
    return ResponseSchema(
        message="Your email has been verified and password is set"
        + (". Please POST to the redirect to get your token" * is_api),
        code=200,
        redirect=request.app.url_path_for("manage_login_api") if is_api else request.app.url_path_for("login"),
    )


@router.get(
    "/queue/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def admin_queue(
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.MANAGE_USERS])],
):
    # ToDo: make a nice page with data
    data = await admin_queue_api(response, user)
    response.status_code = data.code
    return __import__("orjson").dumps(data.model_dump(mode="json"))


@router.get(
    "/queue/.api",
    summary="Queue for verification by admins",
    responses={
        200: {"model": ResponseSchema, "description": "The entire queue"},
    },
    response_class=ORJSONResponse,
)
async def admin_queue_api(
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.MANAGE_USERS])],
) -> UsersResponseSchema:
    all_users: list[MinimalUserSchema] = []
    for db_user in await database.fetch_all(VerificationCodesModel.select()):
        all_users.append(
            MinimalUserSchema(
                user_id=db_user.user_id,
                email=db_user.email,
                displayed_name=db_user.displayed_name,
                age=calculate_age(db_user.birthday),
                scopes=db_user.scopes,
            )
        )

    count = len(all_users)

    response.status_code = 200
    return UsersResponseSchema(
        message=f"Queue containing {count} user{'s'*(count!=1)}",
        code=200,
        count=count,
        users=all_users,
    )


@router.post(
    "/queue/accept",
    summary="Accept a user from queue",
    response_class=ORJSONResponse,
)
async def admin_accept(
    request: Request,
    response: Response,
    user_id: Annotated[UserID, Form()],
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.MANAGE_USERS])],
): ...  # ToDo: accept user


@router.post(
    "/queue/reject",
    summary="Reject a user from queue",
    response_class=ORJSONResponse,
)
async def admin_reject(
    request: Request,
    response: Response,
    user_id: Annotated[UserID, Form()],
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.MANAGE_USERS])],
): ...  # ToDo: reject user
