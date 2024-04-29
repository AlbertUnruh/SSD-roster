from __future__ import annotations


__all__ = (
    "generate_code",
    "verify_code",
)


# standard library
from random import choices

# local
from .database import database
from .models import UserSchema, VerificationCodesModel


# excluding some characters like "I", "O" and "0" to prevent confusion
_CHARACTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_code() -> str:
    return "{}-{}-{}-{}".format(*["".join(choices(_CHARACTERS, k=2)) for _ in range(4)])  # noqa S311


async def verify_code(user: UserSchema, code: str) -> bool:
    return (
        await database.fetch_one(
            VerificationCodesModel.select().where(
                VerificationCodesModel.user_id == user.user_id, VerificationCodesModel.code == code
            )
        )
        is not None
    )
