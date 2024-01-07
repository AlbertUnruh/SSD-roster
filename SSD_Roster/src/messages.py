from __future__ import annotations


__all__ = (
    "flash",
    "get_flashed_messages",
)


# typing
from typing import TypedDict

# fastapi
from fastapi import Request

# local
from .models import MessageCategory


class _MessageDict(TypedDict):
    msg: str
    ctg: MessageCategory


def flash(request: Request, message: str, category: MessageCategory | str = MessageCategory.PRIMARY) -> None:
    category = MessageCategory(category)
    request.session.setdefault("_messages", []).append({"msg": message, "ctg": category})


def get_flashed_messages(request: Request, category: MessageCategory | str = "*") -> list[_MessageDict]:
    if category != "*":
        category = MessageCategory(category)

    to_return = []
    to_keep = []
    for message in request.session.pop("_messages", []):
        if category in ("*", message["ctg"]):
            to_return.append(message)
        else:
            to_keep.append(message)

    request.session["_messages"] = to_keep
    return to_return
