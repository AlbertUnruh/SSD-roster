from __future__ import annotations


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


database = databases.Database(url := settings.DATABASE.URL.unicode_string())
engine = create_engine(url, connect_args={"check_same_thread": False})


async def setup() -> None:
    # local
    from .oauth2 import get_password_hash  # circular import

    DBBaseModel.metadata.create_all(engine)

    # should an owner be created?
    if not settings.DATABASE.CREATE_OWNER:
        pass

    # is an account with the username already present?
    elif await database.fetch_all(UserModel.select().where(UserModel.username == settings.DATABASE.OWNER_USERNAME)):
        pass

    # create the account
    else:
        await database.execute(
            UserModel.insert().values(  # type: ignore
                username=settings.DATABASE.OWNER_USERNAME,
                displayed_name=settings.DATABASE.OWNER_USERNAME,
                email=settings.DATABASE.OWNER_EMAIL,
                email_verified=True,
                user_verified=True,
                birthday=date(2000, 1, 1),
                password=get_password_hash(settings.DATABASE.OWNER_PASSWORD),
                scopes=GroupedScope.OWNER.name,
            )
        )

    # no demo-users allowed?
    if (not settings.ALLOW_DEMO_USERS_IN_DEVELOPMENT) or (settings.ENVIRONMENT != "development"):
        for group in GroupedScope._members():  # noqa
            await database.execute(UserModel.delete().where(UserModel.username == f"demo-{group}"))  # type: ignore

    # demo-users allowed?
    elif settings.ALLOW_DEMO_USERS_IN_DEVELOPMENT:
        for group in GroupedScope._members():  # noqa
            username = f"demo-{group}"
            # create demo-users (if they don't already exist)
            if not await database.fetch_all(UserModel.select().where(UserModel.username == username)):
                await database.execute(
                    UserModel.insert().values(  # type: ignore
                        username=username,
                        displayed_name=username,
                        email=f"{username}@email.example",
                        email_verified=True,
                        user_verified=True,
                        birthday=date(2000, 1, 1),
                        password=get_password_hash(username),
                        scopes=group,
                    )
                )
