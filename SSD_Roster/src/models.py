__all__ = (
    # types
    "UserID",
    "PageID",
    "Year",
    "Week",
    # enums
    "Availability",
    "Weekday",
    # classes
    "RosterModel",
    "TimetableModel",
)


# standard library
from enum import IntEnum

# typing
import annotated_types
from pydantic import BaseModel, NonNegativeInt
from typing import Annotated


# ---------- TYPES ---------- #


UserID = NonNegativeInt
PageID = NonNegativeInt  # for pagination at /timetable/{user_id}?page={N=>0}

Year = Annotated[int, annotated_types.Ge(2023), annotated_types.Le(2100)]
# 2023 is the project's begin and I would be impressed if this project lives until 2100
Week = Annotated[int, annotated_types.Ge(1), annotated_types.Le(53)]
# some years have 53 weeks instead of 52, so they'll be included


# ---------- ENUMS ---------- #


class Availability(IntEnum):
    UNAVAILABLE = 0
    AVAILABLE = 1
    ONLY_IF_REQUIRED = 2


class Weekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4


# ---------- CLASSES ---------- #


class RosterModel(BaseModel):
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


class TimetableModel(BaseModel):
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
