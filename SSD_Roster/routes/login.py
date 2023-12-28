# typing
from pydantic import SecretStr
from typing import Annotated

# fastapi
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse


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
