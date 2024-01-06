from __future__ import annotations

# typing
from typing import Annotated

# fastapi
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

# local
from SSD_Roster.src.oauth2 import authenticate_user, create_access_token


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
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password)
    if user is False:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(sub=user.user_id)

    return {"access_token": access_token, "token_type": "bearer"}
