__all__ = ()


import databases

# local
from .environment import SETTINGS


database = databases.Database(SETTINGS.DATABASE_URL)
