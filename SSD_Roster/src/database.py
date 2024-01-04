__all__ = (
    "database",
    "setup",
)

# standard library
from datetime import date

# third party
import databases
from sqlalchemy import create_engine

# local
from .abc import DBBaseModel
from .environment import settings
from .models import GroupedScope, UserModel
from .oauth2 import get_password_hash


database = databases.Database(url := settings.DATABASE.URL.unicode_string())
engine = create_engine(url, connect_args={"check_same_thread": False})


async def setup() -> bool:
    DBBaseModel.metadata.create_all(engine)

    # should an owner be created?
    if not settings.DATABASE.CREATE_OWNER:
        return False

    # is an account with the username already present?
    if await database.fetch_all(UserModel.select().where(UserModel.username == settings.DATABASE.OWNER_USERNAME)):
        return False

    # create the account
    await database.execute(
        UserModel.insert().values(
            username=settings.DATABASE.OWNER_USERNAME,
            displayed_name=settings.DATABASE.OWNER_USERNAME,
            email=settings.DATABASE.OWNER_EMAIL,
            email_verified=True,
            user_verified=True,
            birthday=date(2000, 1, 1),
            password=get_password_hash(settings.DATABASE.OWNER_PASSWORD),
            scopes=GroupedScope.OWNER,
        )
    )
    return True
