from __future__ import annotations

# standard library
import sys
from io import TextIOWrapper

# typing
from typing import Annotated, AnyStr

# fastapi
from fastapi import APIRouter, Request, Security
from fastapi.responses import HTMLResponse

# local
from SSD_Roster.src.models import Scope, UserSchema
from SSD_Roster.src.oauth2 import get_current_user
from SSD_Roster.src.templates import templates


router = APIRouter(prefix="/logs")


_logs = []
_injected: bool = False


# inject own stdin and stdout
def inject(log_limit: int = 1000):
    global _injected
    if _injected:
        return

    def redirect(to: TextIOWrapper):
        _write = to.write

        def write(s: AnyStr) -> int:
            _logs.append({"source": to.name[1:-1], "message": s})
            if len(_logs) > log_limit:
                _logs.pop(0)
            return _write(s)

        to.write = write
        return to

    sys.stdout = redirect(sys.__stdout__)
    sys.stderr = redirect(sys.__stderr__)
    _injected = True


@router.get(
    "/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def logs(
    request: Request,
    user: Annotated[UserSchema | None, Security(get_current_user, scopes=[Scope.SEE_LOGS])],
):
    # ToDo: make logs able to use "\n" (especially needed for tracebacks as they aren't pretty without linebreaks)
    return templates.TemplateResponse(request, "logs.html", {"logs": _logs, "injected": _injected})
