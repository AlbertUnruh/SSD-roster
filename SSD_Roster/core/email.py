from __future__ import annotations


__all__ = (
    "send",
    "send_verification_email",
)


# third party
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

# typing
from pydantic import EmailStr

# fastapi
from fastapi import Request

# local
from .environment import settings
from .templates import templates
from .utils import might_raise


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
    ok, _ = await might_raise(fastmail.send_message(message), silent)
    return ok and not settings.MAIL.DISABLED


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
                    f"{request.app.url_path_for("verify")}?email={to}&code={code}",
                },
            ).body.decode("utf-8"),
            subtype=MessageType.html,
        ),
    )


# ToDo: send_inventory_finished_email(...); inventory is finished and admins are notified with a list of items (with
#                                           respective stock and warnings if applicable)
# ToDo: send_inventory_expiry_email(...); no user interacted with the inventory, but the system detected an upcoming
#                                         expiration
