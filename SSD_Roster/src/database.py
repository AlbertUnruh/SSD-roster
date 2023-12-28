__all__ = ()


# third party
import databases

# local
from .environment import SETTINGS


database = databases.Database(SETTINGS.DATABASE_URL)
