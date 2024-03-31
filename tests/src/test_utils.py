from __future__ import annotations

# testing
import pytest

# standard library
from datetime import datetime, timedelta, timezone

# typing
from typing import Awaitable, Callable, TypeVar

# local
from SSD_Roster.src import utils


T = TypeVar("T")


async def demo_awaitable(callable: Callable[..., T]) -> T:  # noqa A002
    return callable()


@pytest.mark.parametrize(
    "awaitable, silence, expected",
    [
        (demo_awaitable(lambda: "Hello World!"), True, (True, "Hello World!")),
        (demo_awaitable(lambda: "Hello World!"), False, (True, "Hello World!")),
        (demo_awaitable(lambda: 1 / 0), True, (False, None)),
    ],
)
@pytest.mark.asyncio
async def test_might_raise_passes(awaitable: Awaitable[T], silence: bool, expected: tuple[bool, T | None]):
    assert await utils.might_raise(awaitable, silence) == expected


@pytest.mark.asyncio
async def test_might_raise_raises():
    with pytest.raises(ZeroDivisionError):
        await utils.might_raise(demo_awaitable(lambda: 1 / 0), False)


_utc_now = datetime.now(timezone.utc)


@pytest.mark.parametrize(
    "reference, expected",
    [
        (_utc_now, 0),  # now
        (_utc_now + timedelta(days=1), -1),  # tomorrow
        (_utc_now + timedelta(days=-1), 0),  # yesterday
        (_utc_now.replace(year=_utc_now.year - 1), 1),  # a year ago
        (_utc_now.replace(year=_utc_now.year - 1) + timedelta(days=1), 0),  # a bit less than a year ago
        (_utc_now.replace(year=_utc_now.year + 1), -1),  # in a year
        (_utc_now.replace(year=_utc_now.year + 1) + timedelta(days=1), -2),  # in just a bit more than a year
    ],
)
def test_calculate_age(reference: datetime, expected: int):
    assert utils.calculate_age(reference) == expected
