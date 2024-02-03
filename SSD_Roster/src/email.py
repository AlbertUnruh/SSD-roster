from __future__ import annotations


__all__ = (
    "send",
    "send_verification_email",
)


# standard library
import sys
import traceback

# third party
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

# typing
from pydantic import EmailStr

# fastapi
from fastapi import Request

# local
from .environment import settings
from .templates import templates


fastmail = FastMail(
    ConnectionConfig(
        MAIL_USERNAME=settings.MAIL.USERNAME,
        MAIL_PASSWORD=settings.MAIL.PASSWORD.get_secret_value(),
        MAIL_PORT=settings.MAIL.PORT,
        MAIL_SERVER=settings.MAIL.SERVER,
        MAIL_STARTTLS=settings.MAIL.STARTTLS,
        MAIL_SSL_TLS=settings.MAIL.SSL_TLS,
        MAIL_DEBUG=settings.ENVIRONMENT == "development",
        MAIL_FROM=settings.MAIL.FROM,
        MAIL_FROM_NAME=settings.MAIL.FROM_NAME,
        SUPPRESS_SEND=settings.MAIL.DISABLED,
    )
)


async def send(message: MessageSchema, *, silent: bool = True) -> bool:
    try:
        await fastmail.send_message(message)
    except Exception:  # noqa
        if not silent:
            raise
        sys.stderr.write(traceback.format_exc())  # will get logged
        return False
    return not settings.MAIL.DISABLED


async def send_verification_email(request: Request, to: EmailStr, code: str) -> bool:
    return await send(
        MessageSchema(
            subject="Email Verification",
            recipients=[to],
            body=templates.TemplateResponse(
                request,
                "email/email-verification.html",
                {
                    "code": code,
                    "url": f"{request.base_url.scheme}://{request.base_url.hostname}:{request.base_url.port}"
                    f"{request.app.url_path_for('verify')}?email={to}&code={code}",
                },
            ).body.decode("utf-8"),
            subtype=MessageType.html,
        ),
    )
