from __future__ import annotations

# typing
from pydantic import EmailStr, PastDate
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

# local
from SSD_Roster.src.messages import flash
from SSD_Roster.src.templates import templates


# from SSD_Roster.src.email import send_verification_email


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
    if any((username is None, email is None, birthday is None)):
        response.status_code = 302
        return request.app.url_path_for("register")

    #  await send_registration_email()
    flash(request, f"A code has been sent to {email}. Either enter it here or use the link in the mail.")

    response.status_code = 302
    return request.app.url_path_for("verify") + f"?email={email}"
