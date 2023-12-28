# typing
from pydantic import EmailStr, PastDate
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/register",
    tags=["register"],
)


@router.get(
    "/",
    summary="Displayed page to register",
    response_class=HTMLResponse,
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
