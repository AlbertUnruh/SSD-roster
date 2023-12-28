__all__ = ("Timetable",)


# standard library
from datetime import date

# local
from .models import TimetableSchema


class Timetable(TimetableSchema):
    @property
    def date_range(self) -> tuple[date, date]:
        """Monday and Friday from the given year/week"""
        year, week = self.date_anchor
        return date.fromisocalendar(year, week, 1), date.fromisocalendar(year, week, 5)
