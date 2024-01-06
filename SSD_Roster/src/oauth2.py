from __future__ import annotations


__all__ = (
    "verify_password",
    "get_password_hash",
    "authenticate_user",
    "create_access_token",
)


# standard library
from datetime import datetime, timedelta

# third party
from jwt import decode as jwt_decode
from jwt import encode as jwt_encode
from jwt import PyJWTError
from passlib.context import CryptContext

# typing
from pydantic import SecretStr, ValidationError
from typing import Annotated, Literal, Optional

# fastapi
from fastapi import Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes,
)

# local
from .database import database
from .environment import settings
from .models import GroupedScope, Scope, TokenSchema, UserModel, UserSchema


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes=Scope.to_oauth2_scopes_dict(),
)


def verify_password(
    plain_password: str | SecretStr,
    hashed_password: str | SecretStr,
) -> bool:
    if isinstance(plain_password, SecretStr):
        plain_password = plain_password.get_secret_value()
    if isinstance(hashed_password, SecretStr):
        hashed_password = hashed_password.get_secret_value()
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(
    password: str | SecretStr,
) -> str:
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    return pwd_context.hash(password)


async def authenticate_user(
    username: str,
    password: str | SecretStr,
) -> UserSchema | Literal[False]:
    user: UserModel | None = await database.fetch_one(UserModel.select().where(UserModel.username == username))
    if user is None or user.email_verified is False or user.password is None or user.user_verified is False:
        # can't be authenticated if A user doesn't exist or B the account hasn't finished every verification step
        return False
    if not verify_password(password, user.password):
        return False
    return UserModel.to_schema(user)


def create_access_token(
    sub: str,
    iat: Optional[datetime] = None,
    exp: Optional[datetime] = None,
) -> str:
    if iat is None:
        iat = datetime.utcnow()
    if exp is None:
        exp = datetime.utcnow() + timedelta(hours=settings.TOKEN.LIFETIME)
    return jwt_encode(
        {"sub": sub, "iat": iat, "exp": exp},
        settings.TOKEN.SECRET_KEY.get_secret_value(),
        settings.TOKEN.ALGORITHM,
    )


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserSchema:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": authenticate_value}
    )

    try:
        payload = jwt_decode(token, settings.TOKEN.SECRET_KEY.get_secret_value(), [settings.TOKEN.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = await database.fetch_one(UserModel.select().where(UserModel.user_id == int(user_id)))
        if user is None:
            raise credentials_exception

        token_scopes = []
        for _s in user.scopes.split():  # break down groups
            if ":" in _s:
                token_scopes.append(_s)
            else:
                token_scopes.extend(getattr(GroupedScope, _s).split())
        token_data = TokenSchema(user_id=user_id, scopes=token_scopes)
    except (PyJWTError, ValidationError, ValueError):
        raise credentials_exception  # noqa R100

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            credentials_exception.detail = "Not enough permissions"
            raise credentials_exception
    return UserModel.to_schema(user)
