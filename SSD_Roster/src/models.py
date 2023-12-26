__all__ = (
    "UserID",
    "PageID",
    "Year",
    "Week",
)


from typing import Annotated
import annotated_types

from pydantic import NonNegativeInt


# ---------- TYPES ---------- #

UserID = NonNegativeInt
PageID = NonNegativeInt  # for pagination at /timetable/{user_id}?page={N=>0}

Year = Annotated[int, annotated_types.Ge(2023), annotated_types.Le(2100)]
# 2023 is the project's begin and I would be impressed if this project lives until 2100
Week = Annotated[int, annotated_types.Ge(1), annotated_types.Le(52)]


# ---------- CLASSES ---------- #
...
