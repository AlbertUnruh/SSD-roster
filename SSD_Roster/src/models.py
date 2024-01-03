__all__ = (
    # types
    "UserID",
    "PageID",
    "Year",
    "Week",
    # enums
    "Availability",
    "Weekday",
    "Scope",
    "GroupedScope",
    # schemas
    "RosterSchema",
    "TimetableSchema",
    "TokenSchema",
    "UserSchema",
    # models
    "DBBaseModel",
    "UserModel",
    "RosterModel",
    "TimetableModel",
)


# third party
from aenum import IntEnum, StrEnum, Unique
from sqlalchemy import Boolean, Column, Date, Integer, MetaData, Text
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import registry as sa_registry

# typing
import annotated_types
from pydantic import BaseModel, EmailStr, PastDate, SecretStr
from typing import Annotated, Optional


# ---------- TYPES ---------- #


UserID = Annotated[int, annotated_types.Gt(0)]
PageID = Annotated[int, annotated_types.Gt(0)]  # for pagination at /timetable/{user_id}?page={N>0}

Year = Annotated[int, annotated_types.Ge(2023), annotated_types.Le(2100)]
# 2023 is the project's begin and I would be impressed if this project lives until 2100
Week = Annotated[int, annotated_types.Ge(1), annotated_types.Le(53)]
# some years have 53 weeks instead of 52, so they'll be included


# ---------- ENUMS ---------- #


class Availability(IntEnum, settings=Unique):
    UNAVAILABLE = 0
    AVAILABLE = 1
    ONLY_IF_REQUIRED = 2


class Weekday(IntEnum, settings=Unique):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4


class Scope(StrEnum, settings=Unique, init="value __doc__"):
    # roster
    SEE_ROSTER = "roster:see", "See any published roster."
    DOWNLOAD_ROSTER = "roster:download", "Download any published roster."
    CREATE_ROSTER = "roster:create", "Create a roster."
    SUBMIT_ROSTER = "roster:submit", "Submit a roster to an admin to publish it."
    PUBLISH_ROSTER = "roster:publish", "Publish a submitted roster."

    # calendar
    MANAGE_OWN_CALENDAR = "calendar:manage-own", "Manage a calendar to set own availabilities."
    SEE_OTHERS_CALENDAR = "calendar:see-others", "See calendars of other users."

    # inventory
    SEE_INVENTORY = "inventory:see", "See the inventory."
    MAKE_INVENTORY = "inventory:make", "Make an inventory."
    MANAGE_INVENTORY = "inventory:manage", "Manage the inventory."

    # permissions
    MANAGE_PERMISSIONS = "permissions:manage", "Manage permissions of users."

    # users
    SEE_USERS = "user:see", "See a list of users."
    MANAGE_USERS = "user:manage", "Manage all users."

    # backups
    MANAGE_BACKUPS = "backups:manage", "Manage backups."

    @staticmethod
    def to_oauth2_scopes_dict() -> dict[str, str]:
        return {scope.value: scope.__doc__ for scope in Scope}  # type: ignore


class GroupedScope(StrEnum, init="value __doc__"):
    PUBLIC = Scope.SEE_ROSTER, "Publicly available, no login required."
    USER = (
        " ".join(
            (  # type: ignore
                PUBLIC[0],
                Scope.DOWNLOAD_ROSTER,
                Scope.CREATE_ROSTER,
                Scope.SUBMIT_ROSTER,
                Scope.MANAGE_OWN_CALENDAR,
                Scope.SEE_OTHERS_CALENDAR,
                Scope.SEE_INVENTORY,
                Scope.MAKE_INVENTORY,
                Scope.SEE_USERS,
            )
        ),
        "Available for every user.",
    )
    ADMIN = (
        " ".join(
            (  # type: ignore
                USER[0],
                Scope.PUBLISH_ROSTER,
                Scope.MANAGE_INVENTORY,
                Scope.MANAGE_PERMISSIONS,
                Scope.MANAGE_USERS,
            )
        ),
        "Available for admins for management.",
    )
    OWNER = " ".join(Scope), "Every scope for the owner"


# ---------- SCHEMAS ---------- #


class RosterSchema(BaseModel):
    user_matrix: Annotated[
        list[
            Annotated[
                list[
                    Annotated[
                        list[UserID],
                        annotated_types.MinLen(0),  # this line basically does nothing as length can't be lower than 0
                        annotated_types.MaxLen(3),
                    ]
                ],
                annotated_types.MinLen(4),
                annotated_types.MaxLen(4),
            ]
        ],
        annotated_types.MinLen(5),
        annotated_types.MaxLen(5),
    ] = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    """Will generate a matrix with following dimensions: 5[days]*4[slots]*(0-3)[users]"""
    # A slightly more detailed way to represent the matrix
    # Slot/Day   |Monday     |Tuesday    |Wednesday  |Thursday   |Friday
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #1 (1./2.) |User #1    |User #1    |User #1    |User #1    |User #1
    #            |User #2    |User #2    |User #2    |User #2    |User #2
    #            |User #3    |User #3    |User #3    |User #3    |User #3
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #2 (3./4.) |User #1    |User #1    |User #1    |User #1    |User #1
    #            |User #2    |User #2    |User #2    |User #2    |User #2
    #            |User #3    |User #3    |User #3    |User #3    |User #3
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #3 (5./6.) |User #1    |User #1    |User #1    |User #1    |User #1
    #            |User #2    |User #2    |User #2    |User #2    |User #2
    #            |User #3    |User #3    |User #3    |User #3    |User #3
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #4 (break- |User #1    |User #1    |User #1    |User #1    |User #1
    #     shift) |User #2    |User #2    |User #2    |User #2    |User #2
    #            |User #3    |User #3    |User #3    |User #3    |User #3

    date_anchor: tuple[Year, Week]


class TimetableSchema(BaseModel):
    availability_matrix: Annotated[
        list[
            Annotated[
                list[Availability],
                annotated_types.MinLen(3),
                annotated_types.MaxLen(3),
            ]
        ],
        annotated_types.MinLen(5),
        annotated_types.MaxLen(5),
    ] = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    """Will generate a matrix with following dimensions: 5[days]*3[availabilities]"""
    # A slightly more detailed way to represent the matrix
    # Slot/Day   |Monday     |Tuesday    |Wednesday  |Thursday   |Friday
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #1 (1./2.) |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #2 (3./4.) |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #3 (5./6.) |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]

    date_anchor: tuple[Year, Week]
    user_id: UserID


class TokenSchema(BaseModel):
    user_id: Optional[UserID]
    scopes: list[Scope]


class UserSchema(BaseModel):
    user_id: UserID
    username: str  # only for login
    displayed_name: str
    email: EmailStr
    email_verified: bool  # first you have to verify your email
    user_verified: bool  # then an admin has to verify you
    birthday: PastDate
    password: Optional[SecretStr]  # password will be set once email is verified


# ---------- MODELS ---------- #
class DBBaseModel(metaclass=DeclarativeMeta):
    __tablename__: str
    __abstract__ = True
    registry: sa_registry = sa_registry()
    metadata: MetaData = registry.metadata
    __init__ = registry.constructor


class UserModel(DBBaseModel):
    __tablename__ = "user"

    user_id: Column | UserID = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    username: Column | str = Column(Text, unique=True, nullable=False)
    displayed_name: Column | str = Column(Text, nullable=False)
    email: Column | EmailStr = Column(Text, nullable=False)
    email_verified: Column | bool = Column(Boolean, nullable=False)
    user_verified: Column | bool = Column(Boolean, nullable=False)
    birthday: Column | PastDate = Column(Date, nullable=False)
    password: Column | Optional[SecretStr] = Column(Text, nullable=True)
    scopes: Column | str = Column(Text, nullable=False)


class RosterModel(DBBaseModel):
    __tablename__ = "roster"

    # ID will be YYYYWWPII with YYYY = year, WW = week, P = published and II = increment to prevent duplication
    roster_id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=False, nullable=False)
    year: Column | int = Column(Integer, nullable=False)
    week: Column | int = Column(Integer, nullable=False)
    published: Column | bool = Column(Boolean, nullable=False)
    mo_s1p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_s1p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_s1p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_s2p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_s2p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_s2p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_s3p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_s3p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_s3p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_bp1: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_bp2: Column | Optional[UserID] = Column(Integer, nullable=True)
    mo_bp3: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s1p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s1p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s1p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s2p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s2p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s2p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s3p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s3p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_s3p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_bp1: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_bp2: Column | Optional[UserID] = Column(Integer, nullable=True)
    tu_bp3: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s1p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s1p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s1p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s2p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s2p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s2p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s3p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s3p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_s3p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_bp1: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_bp2: Column | Optional[UserID] = Column(Integer, nullable=True)
    we_bp3: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s1p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s1p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s1p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s2p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s2p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s2p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s3p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s3p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_s3p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_bp1: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_bp2: Column | Optional[UserID] = Column(Integer, nullable=True)
    th_bp3: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s1p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s1p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s1p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s2p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s2p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s2p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s3p1: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s3p2: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_s3p3: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_bp1: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_bp2: Column | Optional[UserID] = Column(Integer, nullable=True)
    fr_bp3: Column | Optional[UserID] = Column(Integer, nullable=True)


class TimetableModel(DBBaseModel):
    __tablename__ = "timetable"

    # ID will be YYYYWWU+ with YYYY = year, WW = week and U+ = user id
    timetable_id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=False, nullable=False)
    mo_s1: Column | Availability = Column(Integer, nullable=False)
    mo_s2: Column | Availability = Column(Integer, nullable=False)
    mo_s3: Column | Availability = Column(Integer, nullable=False)
    mo_b: Column | Availability = Column(Integer, nullable=False)
    tu_s1: Column | Availability = Column(Integer, nullable=False)
    tu_s2: Column | Availability = Column(Integer, nullable=False)
    tu_s3: Column | Availability = Column(Integer, nullable=False)
    tu_b: Column | Availability = Column(Integer, nullable=False)
    we_s1: Column | Availability = Column(Integer, nullable=False)
    we_s2: Column | Availability = Column(Integer, nullable=False)
    we_s3: Column | Availability = Column(Integer, nullable=False)
    we_b: Column | Availability = Column(Integer, nullable=False)
    th_s1: Column | Availability = Column(Integer, nullable=False)
    th_s2: Column | Availability = Column(Integer, nullable=False)
    th_s3: Column | Availability = Column(Integer, nullable=False)
    th_b: Column | Availability = Column(Integer, nullable=False)
    fr_s1: Column | Availability = Column(Integer, nullable=False)
    fr_s2: Column | Availability = Column(Integer, nullable=False)
    fr_s3: Column | Availability = Column(Integer, nullable=False)
    fr_b: Column | Availability = Column(Integer, nullable=False)
