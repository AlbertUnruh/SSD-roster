from __future__ import annotations

# typing
from pydantic import EmailStr, SecretStr
from typing import Annotated, Optional

# fastapi
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.messages import flash
from SSD_Roster.src.models import MessageCategory, UserModel, VerificationCodesModel
from SSD_Roster.src.oauth2 import get_password_hash
from SSD_Roster.src.templates import templates
from SSD_Roster.src.verification import verify_code


router = APIRouter(
    prefix="/verify",
    tags=["verify"],
)


@router.get(
    "/",
    summary="Displayed page to verify",
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
    summary="Registration-manager",
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
