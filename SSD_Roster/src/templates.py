__all__ = ("templates",)


# fastapi
from fastapi.templating import Jinja2Templates


# public instance of Jinja2Templates
templates = Jinja2Templates("templates")
