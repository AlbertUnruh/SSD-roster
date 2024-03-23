from __future__ import annotations

# standard library
from textwrap import dedent

# third party
import jwt
from jwt import PyJWTError

# fastapi
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, Response

# local
from SSD_Roster.src.database import database
from SSD_Roster.src.environment import settings
from SSD_Roster.src.messages import flash
from SSD_Roster.src.models import MessageCategory, UserModel


router = APIRouter(
    prefix="/logout",
    tags=["login"],
)


@router.get(
    "/",
    summary="Endpoint to logout",
    description=dedent(
        """
    This endpoint isn't required for any API, as it just deletes the cookie.
    Logout can be as simple as that.
    """
    ),
    response_class=RedirectResponse,
)
async def logout(
    request: Request,
    response: Response,
):
    if (token := request.cookies.get("token")) is not None:
        response.delete_cookie("token")  # this is the logout process, nothing more, nothing less
        try:
            user_id = jwt.decode(
                token,
                settings.TOKEN.SECRET_KEY.get_secret_value(),
                [settings.TOKEN.ALGORITHM],
                options={"verify_exp": False},
            ).get("sub")
            db_user = await database.fetch_one(UserModel.select().where(UserModel.user_id == int(user_id)))
            if db_user is None:
                raise ValueError
        except (PyJWTError, ValueError):
            # either they've manipulated the token or they got removed from the database /shrug
            flash(request, "Bye, we've just managed to log you out!", MessageCategory.DANGER)
        else:
            user = UserModel.to_schema(db_user)
            # was nicely logged in
            flash(request, f"Bye {user.displayed_name}, you've successfully logged out.", MessageCategory.SUCCESS)
    else:
        # wasn't logged in
        flash(request, "Hello? Bye? Please log in, before you attempt to log out!")
    return request.app.url_path_for("root")
