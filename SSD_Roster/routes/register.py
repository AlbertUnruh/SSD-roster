from __future__ import annotations

# typing
from pydantic import EmailStr, PastDate
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

# local
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
)
async def manage_registration(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    birthday: Annotated[PastDate, Form()],
):
    #  await send_registration_email()
    return f"/!\\ {username}:{email}:{birthday} /!\\"
