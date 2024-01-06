from __future__ import annotations


__all__ = (
    "send",
    "send_email_verification",
)


# third party
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

# typing
from pydantic import EmailStr

# local
from .environment import settings


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
    )
)


async def send(message: MessageSchema) -> None:
    await fastmail.send_message(message)


async def send_email_verification(to: EmailStr, code: str) -> None:
    return await send(
        MessageSchema(
            subject="Email Verification",
            recipients=[to],
            body=f"Here is your code: {code}",
            subtype=MessageType.plain,  # ToDo: add Jinja2 templates for a nicer email
        )
    )
