from __future__ import annotations


__all__ = ("Timetable",)


# standard library
from datetime import date

# typing
import annotated_types
from typing import Annotated

# local
from .models import Availability, TimetableSchema


class Timetable(TimetableSchema):
    @property
    def date_range(self) -> tuple[date, date]:
        """Monday and Friday from the given year/week"""
        year, week = self.date_anchor
        return date.fromisocalendar(year, week, 1), date.fromisocalendar(year, week, 5)

    @staticmethod
    def matrix_from_str1d(
        str1d: Annotated[str, annotated_types.MinLen(20), annotated_types.MaxLen(20)], /
    ) -> Annotated[
        list[
            Annotated[
                list[Availability],
                annotated_types.MinLen(4),
                annotated_types.MaxLen(4),
            ]
        ],
        annotated_types.MinLen(5),
        annotated_types.MaxLen(5),
    ]:
        matrix = []
        for i in range(5):
            matrix.append([])
            for j in range(4):
                matrix[-1].append(str1d[i * 5 + j])
        return matrix
