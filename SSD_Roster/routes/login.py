from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from pydantic import SecretStr


router = APIRouter(
    prefix="/login",
    tags=["login"],
)


@router.get(
    "/",
    summary="Displayed page to login",
    response_class=HTMLResponse,
)
async def login():
    return "press somewhere to log in..."


@router.post(
    "/",
    summary="Login-manager",
)
async def manage_login(
    username: Annotated[str, Form()],
    password: Annotated[SecretStr, Form()],
):
    return f"/!\\ {username}:{password} /!\\"
