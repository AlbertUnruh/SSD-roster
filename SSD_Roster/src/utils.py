from __future__ import annotations


__all__ = ("might_raise",)


# standard library
import sys
import traceback

# typing
from typing import Awaitable, Literal, overload, TypeVar


T = TypeVar("T")


@overload
async def might_raise(awaitable: Awaitable[T], silence: bool = True) -> tuple[bool, T | None]:
    # unspecific with ``bool`` and ``T | None`` for type-hinter
    ...


async def might_raise(
    awaitable: Awaitable[T], silence: bool = True
) -> tuple[Literal[True], T] | tuple[Literal[False], None]:
    """Returns a tuple of (bool, T | None) with bool being True if nothing got raised"""
    try:
        ret = await awaitable
    except Exception:  # noqa
        if not silence:
            raise
        sys.stderr.write("Following exception was silenced")
        sys.stderr.write(traceback.format_exc())  # will get logged
        return False, None
    else:
        return True, ret
