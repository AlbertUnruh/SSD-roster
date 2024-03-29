from __future__ import annotations


__all__ = ("Roster",)


# standard library
from datetime import date

# local
from .models import RosterSchema


class Roster(RosterSchema):
    @property
    def date_range(self) -> tuple[date, date]:
        """Monday and Friday from the given year/week"""
        year, week = self.date_anchor
        return date.fromisocalendar(year, week, 1), date.fromisocalendar(year, week, 5)

    def export_to_pdf(self):  # noqa ANN201
        raise NotImplementedError  # ToDo: use src.pdf.create_roster
