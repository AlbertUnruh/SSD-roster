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
    def matrix_from_form(
        form_data: list[tuple[Annotated[str, annotated_types.MinLen(2), annotated_types.MaxLen(2)], str]], /
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
        data = dict(form_data)
        matrix = []
        for i in range(5):
            matrix.append([])
            for j in range(4):
                matrix[-1].append(Availability(int(data[f"{i}{j}"])))
        return matrix
