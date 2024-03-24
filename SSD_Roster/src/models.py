from __future__ import annotations


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
    "MessageCategory",
    # schemas
    "RosterSchema",
    "TimetableSchema",
    "TokenSchema",
    "MessageSchema",
    "ResponseSchema",
    "RosterResponseSchema",
    "TimetableResponseSchema",
    "UserSchema",
    # models
    "UserModel",
    "RosterModel",
    "TimetableModel",
    "ScopeModel",
    "VerificationCodesModel",
)


# standard library
from datetime import datetime

# third party
from aenum import IntEnum, StrEnum, Unique
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Text

# typing
import annotated_types
from pydantic import BaseModel, EmailStr, PastDate, SecretStr
from typing import Annotated, Optional

# local
from .abc import DBBaseModel, GroupedScopeStr


# ---------- TYPES ---------- #


UserID = Annotated[int, annotated_types.Gt(0)]
PageID = Annotated[int, annotated_types.Ge(0)]  # for pagination (e.g. at /timetable/{user_id}?page={N>=0})

Year = Annotated[int, annotated_types.Ge(datetime.min.year), annotated_types.Le(datetime.max.year)]
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

    # logs
    SEE_LOGS = "logs:see", "See logs."

    @staticmethod
    def to_oauth2_scopes_dict() -> dict[str, str]:
        return {scope.value: scope.__doc__ for scope in Scope}  # type: ignore


class GroupedScope:  # I know, officially not an Enum...
    PUBLIC = GroupedScopeStr("PUBLIC", str(Scope.SEE_ROSTER), "Publicly available, no login required.")

    USER = GroupedScopeStr(
        "USER",
        " ".join(
            (  # type: ignore
                PUBLIC,
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

    ADMIN = GroupedScopeStr(
        "ADMIN",
        " ".join(
            (  # type: ignore
                USER,
                Scope.PUBLISH_ROSTER,
                Scope.MANAGE_INVENTORY,
                Scope.MANAGE_PERMISSIONS,
                Scope.MANAGE_USERS,
            )
        ),
        "Available for admins for management.",
    )

    OWNER = GroupedScopeStr("OWNER", " ".join(Scope), "Every scope for the owner.")

    @classmethod
    def _members(cls) -> dict[str, GroupedScopeStr]:
        return {key: val for key, val in cls.__dict__.items() if key.isupper()}

    @classmethod
    async def sync_with_db(cls) -> None:
        # local
        from .database import database  # circular import

        synced = set()

        # create a record for every scope (if they don't exist)
        for group, _value in cls._members().items():
            _scopes = set(_value.split())
            unsynced_scopes = _scopes - synced
            synced.update(_scopes)

            for scope in unsynced_scopes:
                if (await database.fetch_one(ScopeModel.select().where(ScopeModel.scope == scope))) is None:
                    await database.execute(ScopeModel.insert().values(scope=scope, group_=group))

        grouped_scopes: dict[str, list[str]] = {}

        # now configure the active scopes
        for group in cls._members():
            grouped_scopes[group] = []
            for scope in await database.fetch_all(ScopeModel.select().where(ScopeModel.group_ == group)):
                grouped_scopes[group].append(scope.scope)

        lower_scopes: list[str] = []  # used to let an ADMIN to what a USER can do ect.

        # now actually set the correct values
        for key, value in grouped_scopes.items():
            lower_scopes.extend(value)
            setattr(cls, key, GroupedScopeStr(key, " ".join(lower_scopes), getattr(cls, key).__doc__))


class MessageCategory(StrEnum, settings=Unique):
    PRIMARY = "primary"
    SUCCESS = "success"
    DANGER = "danger"
    ERROR = "error"


# ---------- SCHEMAS ---------- #


class RosterSchema(BaseModel):
    user_matrix: Annotated[
        list[
            Annotated[
                list[
                    Annotated[
                        list[Optional[UserID]],
                        annotated_types.MinLen(3),
                        annotated_types.MaxLen(3),
                    ]
                ],
                annotated_types.MinLen(4),
                annotated_types.MaxLen(4),
            ]
        ],
        annotated_types.MinLen(5),
        annotated_types.MaxLen(5),
    ] = [
        [[None, None, None], [None, None, None], [None, None, None], [None, None, None]],
        [[None, None, None], [None, None, None], [None, None, None], [None, None, None]],
        [[None, None, None], [None, None, None], [None, None, None], [None, None, None]],
        [[None, None, None], [None, None, None], [None, None, None], [None, None, None]],
        [[None, None, None], [None, None, None], [None, None, None], [None, None, None]],
    ]
    """Will generate a matrix with following dimensions: 5[days]*4[shifts]*(0-3)[users]"""
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
    published_by: Optional[UserID]
    published_at: Optional[datetime]

    def to_model(self) -> RosterModel:
        roster_model = RosterModel()
        roster_model.year = self.date_anchor[0]
        roster_model.week = self.date_anchor[1]
        roster_model.published_by = self.published_by
        roster_model.published_at = self.published_at
        roster_model.mo_s1p1 = self.user_matrix[0][0][0]
        roster_model.mo_s1p2 = self.user_matrix[0][0][1]
        roster_model.mo_s1p3 = self.user_matrix[0][0][2]
        roster_model.mo_s2p1 = self.user_matrix[0][1][0]
        roster_model.mo_s2p2 = self.user_matrix[0][1][1]
        roster_model.mo_s2p3 = self.user_matrix[0][1][2]
        roster_model.mo_s3p1 = self.user_matrix[0][2][0]
        roster_model.mo_s3p2 = self.user_matrix[0][2][1]
        roster_model.mo_s3p3 = self.user_matrix[0][2][2]
        roster_model.mo_bp1 = self.user_matrix[0][3][0]
        roster_model.mo_bp2 = self.user_matrix[0][3][1]
        roster_model.mo_bp3 = self.user_matrix[0][3][2]
        roster_model.tu_s1p1 = self.user_matrix[1][0][0]
        roster_model.tu_s1p2 = self.user_matrix[1][0][1]
        roster_model.tu_s1p3 = self.user_matrix[1][0][2]
        roster_model.tu_s2p1 = self.user_matrix[1][1][0]
        roster_model.tu_s2p2 = self.user_matrix[1][1][1]
        roster_model.tu_s2p3 = self.user_matrix[1][1][2]
        roster_model.tu_s3p1 = self.user_matrix[1][2][0]
        roster_model.tu_s3p2 = self.user_matrix[1][2][1]
        roster_model.tu_s3p3 = self.user_matrix[1][2][2]
        roster_model.tu_bp1 = self.user_matrix[1][3][0]
        roster_model.tu_bp2 = self.user_matrix[1][3][1]
        roster_model.tu_bp3 = self.user_matrix[1][3][2]
        roster_model.we_s1p1 = self.user_matrix[2][0][0]
        roster_model.we_s1p2 = self.user_matrix[2][0][1]
        roster_model.we_s1p3 = self.user_matrix[2][0][2]
        roster_model.we_s2p1 = self.user_matrix[2][1][0]
        roster_model.we_s2p2 = self.user_matrix[2][1][1]
        roster_model.we_s2p3 = self.user_matrix[2][1][2]
        roster_model.we_s3p1 = self.user_matrix[2][2][0]
        roster_model.we_s3p2 = self.user_matrix[2][2][1]
        roster_model.we_s3p3 = self.user_matrix[2][2][2]
        roster_model.we_bp1 = self.user_matrix[2][3][0]
        roster_model.we_bp2 = self.user_matrix[2][3][1]
        roster_model.we_bp3 = self.user_matrix[2][3][2]
        roster_model.th_s1p1 = self.user_matrix[3][0][0]
        roster_model.th_s1p2 = self.user_matrix[3][0][1]
        roster_model.th_s1p3 = self.user_matrix[3][0][2]
        roster_model.th_s2p1 = self.user_matrix[3][1][0]
        roster_model.th_s2p2 = self.user_matrix[3][1][1]
        roster_model.th_s2p3 = self.user_matrix[3][1][2]
        roster_model.th_s3p1 = self.user_matrix[3][2][0]
        roster_model.th_s3p2 = self.user_matrix[3][2][1]
        roster_model.th_s3p3 = self.user_matrix[3][2][2]
        roster_model.th_bp1 = self.user_matrix[3][3][0]
        roster_model.th_bp2 = self.user_matrix[3][3][1]
        roster_model.th_bp3 = self.user_matrix[3][3][2]
        roster_model.fr_s1p1 = self.user_matrix[4][0][0]
        roster_model.fr_s1p2 = self.user_matrix[4][0][1]
        roster_model.fr_s1p3 = self.user_matrix[4][0][2]
        roster_model.fr_s2p1 = self.user_matrix[4][1][0]
        roster_model.fr_s2p2 = self.user_matrix[4][1][1]
        roster_model.fr_s2p3 = self.user_matrix[4][1][2]
        roster_model.fr_s3p1 = self.user_matrix[4][2][0]
        roster_model.fr_s3p2 = self.user_matrix[4][2][1]
        roster_model.fr_s3p3 = self.user_matrix[4][2][2]
        roster_model.fr_bp1 = self.user_matrix[4][3][0]
        roster_model.fr_bp2 = self.user_matrix[4][3][1]
        roster_model.fr_bp3 = self.user_matrix[4][3][2]
        return roster_model


class TimetableSchema(BaseModel):
    availability_matrix: Annotated[
        list[
            Annotated[
                list[Availability],
                annotated_types.MinLen(4),
                annotated_types.MaxLen(4),
            ]
        ],
        annotated_types.MinLen(5),
        annotated_types.MaxLen(5),
    ] = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    """Will generate a matrix with following dimensions: 5[days]*4[availabilities]"""
    # A slightly more detailed way to represent the matrix
    # Slot/Day   |Monday     |Tuesday    |Wednesday  |Thursday   |Friday
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #1 (1./2.) |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #2 (3./4.) |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #3 (5./6.) |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]
    # -----------+-----------+-----------+-----------+-----------+-----------
    # #4 (break) |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]  |Y/N/[...]

    date_anchor: tuple[Year, Week]
    user_id: UserID

    def to_model(self) -> TimetableModel:
        timetable_model = TimetableModel()
        timetable_model.user_id = self.user_id
        timetable_model.year = self.date_anchor[0]
        timetable_model.week = self.date_anchor[1]
        timetable_model.mo_s1 = self.availability_matrix[0][0]
        timetable_model.mo_s2 = self.availability_matrix[0][1]
        timetable_model.mo_s3 = self.availability_matrix[0][2]
        timetable_model.mo_b = self.availability_matrix[0][3]
        timetable_model.tu_s1 = self.availability_matrix[1][0]
        timetable_model.tu_s2 = self.availability_matrix[1][1]
        timetable_model.tu_s3 = self.availability_matrix[1][2]
        timetable_model.tu_b = self.availability_matrix[1][3]
        timetable_model.we_s1 = self.availability_matrix[2][0]
        timetable_model.we_s2 = self.availability_matrix[2][1]
        timetable_model.we_s3 = self.availability_matrix[2][2]
        timetable_model.we_b = self.availability_matrix[2][3]
        timetable_model.th_s1 = self.availability_matrix[3][0]
        timetable_model.th_s2 = self.availability_matrix[3][1]
        timetable_model.th_s3 = self.availability_matrix[3][2]
        timetable_model.th_b = self.availability_matrix[3][3]
        timetable_model.fr_s1 = self.availability_matrix[4][0]
        timetable_model.fr_s2 = self.availability_matrix[4][1]
        timetable_model.fr_s3 = self.availability_matrix[4][2]
        timetable_model.fr_b = self.availability_matrix[4][3]
        return timetable_model


class TokenSchema(BaseModel):
    user_id: UserID
    scopes: list[Scope]


class MessageSchema(BaseModel):
    message: str
    category: MessageCategory = MessageCategory.PRIMARY


class ResponseSchema(BaseModel):
    message: str
    code: Annotated[int, annotated_types.Ge(100), annotated_types.Lt(600)]

    # optional
    redirect: str = ""


class RosterResponseSchema(ResponseSchema):
    roster: RosterSchema


class TimetableResponseSchema(ResponseSchema):
    timetable: TimetableSchema


class UserSchema(BaseModel):
    user_id: UserID
    username: str  # only for login
    displayed_name: str
    email: EmailStr
    email_verified: bool  # first you have to verify your email
    user_verified: bool  # then an admin has to verify you
    birthday: PastDate
    password: Optional[SecretStr]  # password will be set once email is verified
    scopes: str

    def to_model(self) -> UserModel:
        user_model = UserModel()
        user_model.user_id = self.user_id
        user_model.username = self.username
        user_model.displayed_name = self.displayed_name
        user_model.email = self.email
        user_model.email_verified = self.email_verified
        user_model.user_verified = self.user_verified
        user_model.birthday = self.birthday
        user_model.password = self.password
        user_model.scopes = self.scopes
        return user_model


# ---------- MODELS ---------- #


class UserModel(DBBaseModel):
    __tablename__ = "user"

    user_id: Column | UserID = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    username: Column | str = Column(Text, unique=True, nullable=False)
    displayed_name: Column | str = Column(Text, nullable=False)
    email: Column | EmailStr = Column(Text, unique=True, nullable=False)
    email_verified: Column | bool = Column(Boolean, nullable=False)
    user_verified: Column | bool = Column(Boolean, nullable=False)
    birthday: Column | PastDate = Column(Date, nullable=False)
    password: Column | Optional[SecretStr] = Column(Text, nullable=True)
    scopes: Column | str = Column(Text, nullable=False)

    @staticmethod  # SQLAlchemy tries to find a column...
    def to_schema(self: UserModel) -> UserSchema:
        return UserSchema(
            user_id=self.user_id,
            username=self.username,
            displayed_name=self.displayed_name,
            email=self.email,
            email_verified=self.email_verified,
            user_verified=self.user_verified,
            birthday=self.birthday,
            password=self.password,
            scopes=self.scopes,
        )


class RosterModel(DBBaseModel):
    __tablename__ = "roster"

    roster_id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    year: Column | Year = Column(Integer, nullable=False)
    week: Column | Week = Column(Integer, nullable=False)
    published: Column | bool = Column(Boolean, nullable=False)
    published_by: Column | UserID = Column(Integer, nullable=False)
    published_at: Column | datetime = Column(DateTime, nullable=False)
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

    @staticmethod  # SQLAlchemy tries to find a column...
    def to_schema(self: RosterModel) -> RosterSchema:
        return RosterSchema(
            user_matrix=[
                [
                    [self.mo_s1p1, self.mo_s1p2, self.mo_s1p3],
                    [self.mo_s2p1, self.mo_s2p2, self.mo_s2p3],
                    [self.mo_s3p1, self.mo_s3p2, self.mo_s3p3],
                    [self.mo_bp1, self.mo_bp2, self.mo_bp3],
                ],
                [
                    [self.tu_s1p1, self.tu_s1p2, self.tu_s1p3],
                    [self.tu_s2p1, self.tu_s2p2, self.tu_s2p3],
                    [self.tu_s3p1, self.tu_s3p2, self.tu_s3p3],
                    [self.tu_bp1, self.tu_bp2, self.tu_bp3],
                ],
                [
                    [self.we_s1p1, self.we_s1p2, self.we_s1p3],
                    [self.we_s2p1, self.we_s2p2, self.we_s2p3],
                    [self.we_s3p1, self.we_s3p2, self.we_s3p3],
                    [self.we_bp1, self.we_bp2, self.we_bp3],
                ],
                [
                    [self.th_s1p1, self.th_s1p2, self.th_s1p3],
                    [self.th_s2p1, self.th_s2p2, self.th_s2p3],
                    [self.th_s3p1, self.th_s3p2, self.th_s3p3],
                    [self.th_bp1, self.th_bp2, self.th_bp3],
                ],
                [
                    [self.fr_s1p1, self.fr_s1p2, self.fr_s1p3],
                    [self.fr_s2p1, self.fr_s2p2, self.fr_s2p3],
                    [self.fr_s3p1, self.fr_s3p2, self.fr_s3p3],
                    [self.fr_bp1, self.fr_bp2, self.fr_bp3],
                ],
            ],
            date_anchor=(self.year, self.week),
            published_by=self.published_by,
            published_at=self.published_at,
        )


class TimetableModel(DBBaseModel):
    __tablename__ = "timetable"

    timetable_id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    user_id: Column | UserID = Column(Integer, nullable=False)
    year: Column | Year = Column(Integer, nullable=False)
    week: Column | Week = Column(Integer, nullable=False)
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

    @staticmethod  # SQLAlchemy tries to find a column...
    def to_schema(self: TimetableModel) -> TimetableSchema:
        return TimetableSchema(
            availability_matrix=[
                [self.mo_s1, self.mo_s2, self.mo_s3, self.mo_b],
                [self.tu_s1, self.tu_s2, self.tu_s3, self.tu_b],
                [self.we_s1, self.we_s2, self.we_s3, self.we_b],
                [self.th_s1, self.th_s2, self.th_s3, self.th_b],
                [self.fr_s1, self.fr_s2, self.fr_s3, self.fr_b],
            ],
            date_anchor=(self.year, self.week),
            user_id=self.user_id,
        )


class ScopeModel(DBBaseModel):
    __tablename__ = "scopes"

    scope: Column | str = Column(Text, primary_key=True, unique=True, nullable=False)
    group_: Column | str = Column(Text, nullable=False)


class VerificationCodesModel(DBBaseModel):
    __tablename__ = "verification_code"

    user_id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=False, nullable=False)
    email: Column | str = Column(Text, nullable=False)
    code: Column | str = Column(Text, nullable=False)
