from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from pydantic import EmailStr, PastDate

router = APIRouter(
    prefix="/register",
    tags=["register"],
)


@router.get(
    "/",
    summary="Displayed page to register",
)
async def register():
    return "press somewhere to register..."


@router.post(
    "/",
    summary="Registration-manager",
)
async def manage_registration(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    birthday: Annotated[PastDate, Form()],
):
    return f"/!\\ {username}:{email}:{birthday} /!\\"
