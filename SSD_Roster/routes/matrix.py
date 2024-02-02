from __future__ import annotations

# fastapi
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

# local
from SSD_Roster.src.templates import templates


router = APIRouter(prefix="/nice ports,")


@router.get(
    "/Trinity.txt.bak",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def trinity(request: Request):
    # this is just an easter-egg
    # *and something to confuse nmap's scan a bit as I'm not returning a 404 (:*
    return templates.TemplateResponse(request, "matrix.html")
