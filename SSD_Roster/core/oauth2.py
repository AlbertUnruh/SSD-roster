from __future__ import annotations


__all__ = (
    "verify_password",
    "get_password_hash",
    "authenticate_user",
    "create_access_token",
    "get_current_user",
)


# standard library
from datetime import datetime, timedelta, timezone

# third party
from jwt import decode as jwt_decode
from jwt import encode as jwt_encode
from jwt import PyJWTError
from passlib.context import CryptContext

# typing
from pydantic import SecretStr, ValidationError
from typing import Annotated, Literal, Optional

# fastapi
from fastapi import Cookie, Depends, HTTPException
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
    tokenUrl="token",
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
    scopes: Optional[str] = None,
    iat: Optional[datetime] = None,
    exp: Optional[datetime] = None,
) -> str:
    if scopes is None:
        scopes = ""
    if isinstance(scopes, list):
        scopes = " ".join(scopes)
    if iat is None:
        iat = datetime.utcnow().replace(tzinfo=timezone.utc)
    if exp is None:
        exp = (datetime.utcnow() + timedelta(hours=settings.TOKEN.LIFETIME)).replace(tzinfo=timezone.utc)
    return jwt_encode(
        {"sub": sub, "scopes": scopes, "iat": iat, "exp": exp},
        settings.TOKEN.SECRET_KEY.get_secret_value(),
        settings.TOKEN.ALGORITHM,
    )


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme), Cookie()] = "PUBLIC",
) -> UserSchema | None:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": authenticate_value}
    )

    if token == "PUBLIC":  # noqa S105  # not a password, but a default
        # a public user; ID isn't accessed --> can have any value
        token_data = TokenSchema(user_id=69, scopes=GroupedScope.PUBLIC.split())
        user = None

        # skip first validation loop as every granted scope is available for public users
        token_scopes = []
        user_scopes = []

    else:
        try:
            payload = jwt_decode(token, settings.TOKEN.SECRET_KEY.get_secret_value(), [settings.TOKEN.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise credentials_exception

            token_scopes = []
            for _s in payload.get("scopes", "").split():  # break down groups
                if ":" in _s:
                    token_scopes.append(_s)
                else:
                    token_scopes.extend(getattr(GroupedScope, _s).split())
            token_data = TokenSchema(user_id=user_id, scopes=token_scopes)
        except (PyJWTError, ValidationError):
            raise credentials_exception  # noqa R100

        user = await database.fetch_one(UserModel.select().where(UserModel.user_id == token_data.user_id))
        if user is None:
            raise credentials_exception
        user = UserModel.to_schema(user)

        user_scopes = []
        for _s in user.scopes.split():
            if ":" in _s:
                user_scopes.append(_s)
            else:
                user_scopes.extend(getattr(GroupedScope, _s).split())

    credentials_exception.detail = "Not enough permissions"

    # check if token-requested scopes are granted for the user
    for token_scope in token_scopes:
        if token_scope not in user_scopes:
            raise credentials_exception

    # check if security-requested scopes are granted for the token
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise credentials_exception

    return user
