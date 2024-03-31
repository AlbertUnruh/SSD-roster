from __future__ import annotations

# testing
from pytest import fixture


@fixture()
def username_user() -> str:
    return "Alice"


@fixture()
def password_user() -> str:
    return "Password1234"
