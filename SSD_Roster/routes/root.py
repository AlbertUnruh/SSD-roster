from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(
    tags=["root"],
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def root():
    return "[CURRENT ROSTER]\n[LOGIN]"
