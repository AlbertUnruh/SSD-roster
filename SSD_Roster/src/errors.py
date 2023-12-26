__all__ = (
    "SSDRosterError",
    "DeveloperError",
    "InternalNotImplementedError",
    "DeveloperArgumentError",
    "UnrecognisedPermissionLevelError",
    "InvalidPermissionLevelError",
    "UnrecognisedBooleanError",
    "TranslationError",
    "UnsupportedTranslationTypeError",
    "UnsupportedLanguageError",
    "DatabaseError",
    "NoActiveSessionError",
)


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional


class SSDRosterError(Exception):
    """
    Base for every Exception from SSD-roster.
    """


class DeveloperError(SSDRosterError):
    pass


class InternalNotImplementedError(DeveloperError, NotImplementedError):
    func_o_meth_o_mod: str
    """--> Function or Method or Module"""

    def __init__(self, func_o_meth_o_mod: str):
        self.func_o_meth_o_mod = func_o_meth_o_mod

    def __str__(self) -> str:
        return f"{self.func_o_meth_o_mod} is not implemented!"


class DeveloperArgumentError(DeveloperError):
    pass


class UnrecognisedPermissionLevelError(DeveloperArgumentError, ValueError):
    level: int

    def __init__(self, level: int):
        self.level = level

    def __str__(self) -> str:
        return f"Permission level {self.level} not found!"


class InvalidPermissionLevelError(DeveloperArgumentError, ValueError):
    level: int

    def __init__(self, level: int):
        self.level = level

    def __str__(self) -> str:
        return f"Permission level has to be higher than 0 and not {self.level}!"


class UnrecognisedBooleanError(SSDRosterError):
    obj: object

    def __init__(self, obj: object):
        self.obj = obj

    def __str__(self) -> str:
        return f"Unable to assign {self.obj.__class__.__qualname__} with value {self.obj!r} to either True or False!"


class TranslationError(SSDRosterError):
    pass


class UnsupportedTranslationTypeError(TranslationError):
    key: str
    type: object  # noqa: A003
    supported: list[object]

    def __init__(self, key: str, type: object, supported: Optional[list[object]] = None):  # noqa: A002
        self.key = key
        self.type = type
        if supported is None:
            self.supported = []
        else:
            self.supported = supported

    def __str__(self) -> str:
        return f"Unsupported type {self.type!r} for {self.key!r}!" + (
            f" Following types are supported: {', '.join(f'{s!r}' for s in self.supported)}" if self.supported else ""
        )


class UnsupportedLanguageError(TranslationError):
    language: str
    supported: list[str]

    def __init__(self, language: str, supported: Optional[list[str]] = None):
        self.language = language
        if supported is None:
            from .settings import Settings

            self.supported = Settings.LANGUAGE_AVAILABLE
        else:
            self.supported = supported

    def __str__(self) -> str:
        return f"Unsupported language {self.language!r}! Supported languages are: {', '.join(self.supported)}"


class DatabaseError(SSDRosterError):
    pass


class NoActiveSessionError(DatabaseError):
    def __str__(self) -> str:
        return "There is no active database session in this context!"
