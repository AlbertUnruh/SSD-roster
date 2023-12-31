__all__ = (
    "exception_handler",
    "validation_exception_handler",
)


# fastapi
from fastapi.exceptions import RequestValidationError
from fastapi.openapi import utils as openapi_utils
from fastapi.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY

# local
from .environment import settings
from .templates import templates


if settings.OVERRIDE_422_WITH_400:
    # change the status from 422 to 400 by overriding the imported variable
    openapi_utils.HTTP_422_UNPROCESSABLE_ENTITY = HTTP_400_BAD_REQUEST


async def exception_handler(request: Request, exc: StarletteHTTPException):  # noqa ANN201
    code = exc.status_code
    return templates.TemplateResponse(
        request,
        "error-page.html",
        {"code": code, "detail": exc.detail},
        code,
        exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):  # noqa ANN201
    code, detail = (
        (HTTP_400_BAD_REQUEST, "Bad Request")
        if settings.OVERRIDE_422_WITH_400
        else (HTTP_422_UNPROCESSABLE_ENTITY, "Unprocessable Entity")
    )
    return templates.TemplateResponse(
        request,
        "error-page.html",
        {"code": code, "detail": detail},
        code,
        {"X-Debug-Description": str(exc)},
    )
