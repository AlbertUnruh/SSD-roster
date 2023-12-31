__all__ = ()


# third party
import databases

# local
from .environment import settings


database = databases.Database(settings.DATABASE_URL)
