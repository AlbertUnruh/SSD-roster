from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from SSD_Roster.src.templates import templates


router = APIRouter()


@router.get(
    "/",
    include_in_schema=False,
    response_class=HTMLResponse,
)
async def root(request: Request):
    # return "[CURRENT ROSTER]\n[LOGIN]"
    return templates.TemplateResponse(request, "base.html")  # ToDo: remove this line as it's just for testing
