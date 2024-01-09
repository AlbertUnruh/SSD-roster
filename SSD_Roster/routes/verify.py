from __future__ import annotations

# typing
from pydantic import EmailStr, SecretStr
from typing import Annotated, Optional

# fastapi
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

# local
from SSD_Roster.src.templates import templates


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
    if any((email is None, code is None, password is None)):
        response.status_code = 302
        return request.app.url_path_for("verify") + f"?email={email or ''}&code={code or ''}"

    # ToDo: verify email/code; set password; redirect to /users/me
    return HTMLResponse(f"/!\\ {email}:{code}:{password} /!\\")
