from __future__ import annotations

# testing
from pytest import fixture
from smtp_test_server.context import SmtpMockServer

# standard library
import os


@fixture(scope="session")
def username_user() -> str:
    return "Alice"


@fixture(scope="session")
def password_user() -> str:
    return "Password1234"


@fixture(scope="session")
def email_user(username_user: str) -> str:
    return f"{username_user.lower()}@test.org"


@fixture(scope="function")
def smtp_server() -> SmtpMockServer:
    with SmtpMockServer(os.environ["MAIL__SERVER"], int(os.environ["MAIL__PORT"])) as stmp_mock_server:
        yield stmp_mock_server
