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
from SSD_Roster.src.models import MessageCategory, Scope, UserID, UserModel, UserSchema, VerificationCodesModel
from SSD_Roster.src.oauth2 import get_current_user, get_password_hash
from SSD_Roster.src.templates import templates
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
    # ToDo: make a .api-variant
    # summary="Registration-manager",
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
    # everything set?
    if any((email is None, code is None, password is None)):
        response.status_code = 302
        return request.app.url_path_for("verify") + f"?email={email or ''}&code={code or ''}"

    # invalid email?
    if (user := await database.fetch_one(UserModel.select().where(UserModel.email == email))) is None:
        flash(request, f"Invalid email {email}!", MessageCategory.ERROR)
        response.status_code = 302
        return request.app.url_path_for("verify") + f"?email={email or ''}&code={code or ''}"

    # invalid code?
    if not await verify_code(user, code):
        flash(request, f"Invalid code {code}!", MessageCategory.ERROR)
        response.status_code = 302
        return request.app.url_path_for("verify") + f"?email={email or ''}&code={code or ''}"

    # set password
    await database.execute(
        UserModel.update()  # type: ignore
        .where(UserModel.email == user.email)
        .values(password=get_password_hash(password), email_verified=True)
    )

    flash(request, "Your email has been verified and password is set", MessageCategory.SUCCESS)

    await database.execute(VerificationCodesModel.delete().where(VerificationCodesModel.user_id == user.user_id))

    response.status_code = 302
    return request.app.url_path_for("login")


@router.get(
    "/queue/",
    # ToDo: make a .api-variant
    # summary="Queue for verification by admins",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def admin_queue(
    request: Request,
    response: Response,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.MANAGE_USERS])],
): ...  # ToDo: get queue


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
