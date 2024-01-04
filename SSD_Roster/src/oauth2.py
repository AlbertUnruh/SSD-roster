from __future__ import annotations


__all__ = (
    "verify_password",
    "get_password_hash",
    "authenticate_user",
)


# isort: skip_file
# I want the imports just a little bit longer all in here, will remove `noqa`s afterward...
from datetime import datetime, timedelta  # noqa
from typing import Annotated, Optional, Literal  # noqa
from fastapi import Depends, FastAPI, HTTPException, Security, status  # noqa
from fastapi.security import (  # noqa
    OAuth2PasswordBearer,  # noqa
    OAuth2PasswordRequestForm,  # noqa
    SecurityScopes,  # noqa
)  # noqa
from passlib.context import CryptContext  # noqa
from pydantic import BaseModel, SecretStr, ValidationError  # noqa
from .models import UserID, Scope, TokenSchema, UserSchema  # noqa


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes=Scope.to_oauth2_scopes_dict(),
)


def verify_password(plain_password: str | SecretStr, hashed_password: str | SecretStr) -> bool:
    if isinstance(plain_password, SecretStr):
        password = password._secret_value  # noqa
    if isinstance(hashed_password, SecretStr):
        password = password._secret_value  # noqa
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str | SecretStr) -> str:
    if isinstance(password, SecretStr):
        password = password._secret_value  # noqa
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> UserSchema | Literal[False]:
    user: UserSchema | None = NotImplemented
    if user is None or user.email_verified is False or user.password is None or user.user_verified is False:
        # can't be authenticated if A user doesn't exist or B the account hasn't finished every verification step
        return False
    if not verify_password(password, user.password):  # type: ignore
        return False
    return user
