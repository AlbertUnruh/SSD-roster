from __future__ import annotations


__all__ = ("patch_passlib",)


# standard library
import inspect

# third party
import passlib


def patch_passlib():
    if passlib.__version__ == "1.7.4":  # noqa
        code = inspect.getsource(passlib.handlers.bcrypt._BcryptBackend)  # noqa
        code = code.replace(
            """\
        try:
            version = _bcrypt.__about__.__version__
        except:
            log.warning("(trapped) error reading bcrypt version", exc_info=True)
            version = '<unknown>'""",
            """\
        version = getattr(getattr(_bcrypt, '__about__', _bcrypt), '__version__', '<unknown>')""",
        )
        env = {
            k: getattr(passlib.handlers.bcrypt, k)  # noqa
            for k in ("_BcryptCommon", "_detect_pybcrypt", "log", "unicode")
        }
        exec(code, env)  # noqa S102
        passlib.handlers.bcrypt._BcryptBackend._load_backend_mixin = env["_BcryptBackend"]._load_backend_mixin  # noqa
        passlib.handlers.bcrypt.bcrypt._backend_mixin_map["bcrypt"] = env["_BcryptBackend"]  # noqa
        passlib.__version__ += "-patch"  # noqa
