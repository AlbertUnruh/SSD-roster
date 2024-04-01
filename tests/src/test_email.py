from __future__ import annotations

# testing
import pytest
from smtp_test_server.context import SmtpMockServer

# standard library
from base64 import b64encode

# third party
from fastapi_mail import MessageSchema, MessageType

# local
from SSD_Roster.src import email


def test_config():
    # to make sure that the following tests work as expected
    assert not email.fastmail.config.SUPPRESS_SEND
    assert not email.fastmail.config.USE_CREDENTIALS


@pytest.mark.asyncio
async def test_send(smtp_server: SmtpMockServer, email_user: str):
    assert len(smtp_server.messages) == 0
    assert (
        await email.send(
            MessageSchema(
                subject="Test Email",
                recipients=[email_user],
                body=b"This is a test email!",
                subtype=MessageType.plain,
            )
        )
        is True
    )
    assert len(smtp_server.messages) == 1
    assert smtp_server.messages[0].get("From") == "GymPap - SSD <no-reply@test.org>"
    assert smtp_server.messages[0].get("To") == email_user
    assert smtp_server.messages[0].get("Subject") == "Test Email"
    assert smtp_server.messages[0].get_payload()[0]._headers[0][0] == "Content-Type"
    assert smtp_server.messages[0].get_payload()[0]._headers[0][1] == 'text/plain; charset="utf-8"'
    assert smtp_server.messages[0].get_payload()[0]._headers[2][0] == "Content-Transfer-Encoding"
    assert smtp_server.messages[0].get_payload()[0]._headers[2][1] == "base64"
    assert smtp_server.messages[0].get_payload()[0]._payload == b64encode(b"This is a test email!").decode() + "\r\n"


@pytest.mark.asyncio
async def test_send_suppressed(smtp_server: SmtpMockServer, email_user: str, monkeypatch):  # noqa: ANN001
    monkeypatch.setattr(email.fastmail.config, "SUPPRESS_SEND", True)
    assert len(smtp_server.messages) == 0
    assert (
        await email.send(
            MessageSchema(
                subject="Test Email",
                recipients=[email_user],
                body=b"This is email won't be sent!",
                subtype=MessageType.plain,
            )
        )
        is False
    )
    assert len(smtp_server.messages) == 0
