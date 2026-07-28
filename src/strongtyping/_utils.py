import logging
import os
from _ctypes import sizeof
from collections.abc import Callable, Mapping, Sequence
from string import Template
from types import MethodType
from typing import Any, ParamSpec, TypeVar

from strongtyping.config import SEVERITY_LEVEL

T = TypeVar("T")
P = ParamSpec("P")

logger = logging.getLogger(__name__)

ORIGINAL_DUCK_TYPES: Any = {
    int: [int, float, complex],
    float: [float, complex],
    bytearray: [bytearray, bytes],
}


CACHE_IGNORE_CLASS_FUNCTIONS = ("__init__",)

_error_info_msg = Template(
    "TypeMismatch: failed at $source\nExpected type: $expected_type\nActual value: $actual_value (type: $actual_type)"
)


def get_safe_cache_key(
    args: Sequence[Any], kwargs: Mapping[Any, Any]
) -> tuple[tuple[int | str, ...], tuple[int | str, ...]]:
    try:
        # Only use string representation if objects are small/primitive
        # to avoid massive string allocation overhead
        arg_vals = tuple(repr(arg) if sizeof(arg) < 1024 else id(arg) for arg in args)
        kwarg_vals = tuple(repr(kwarg) if sizeof(kwarg) < 1024 else id(kwarg) for kwarg in kwargs)
        return arg_vals, kwarg_vals
    except TypeError:
        try:
            # mostly when args or kwargs contain objects that are not supporting sizeof
            arg_vals = tuple(repr(arg) for arg in args)
            kwarg_vals = tuple(repr(kwarg) for kwarg in kwargs)
            return arg_vals, kwarg_vals
        except Exception:  # noqa: BLE001
            return tuple(id(arg) for arg in args), tuple(id(kwarg) for kwarg in kwargs)


def remove_subclass(args: Any, subclass: bool) -> Any:
    if len(args) == 1:
        return args
    cls = args[0] if subclass else None
    if cls is not None:
        args = args[1:]
    return args


SEVERITY_CONFIG = {
    "warning": SEVERITY_LEVEL.WARNING,
    "disable": SEVERITY_LEVEL.DISABLED,
    "enable": SEVERITY_LEVEL.ENABLED,
}


def get_severity_level(severity_: str | SEVERITY_LEVEL) -> int:
    if severity_ == "env":
        _level = os.environ.get("ST_SEVERITY", "1")
        try:
            return int(_level)
        except (TypeError, ValueError):
            level = SEVERITY_CONFIG.get(_level, SEVERITY_LEVEL.ENABLED)
            return level.value
    else:
        return int(severity_.value) if isinstance(severity_, SEVERITY_LEVEL) else int(severity_)


exclude_builtins = dir(object)


def _get_new(
    typing_func: Callable[..., Any],
    excep_raise: type[Exception] = TypeError,
    cache_size: int = 0,
    severity: str = "env",
    **kwargs: Any,
) -> Any:
    def new_with_match_typing(cls_: type[T], *args: Any, **kwargs: Any) -> T:
        def add_match_typing(obj: T, attr: str) -> bool:
            if (
                hasattr(getattr(cls_, attr), "__annotations__")
                and getattr(cls_, attr).__class__.__name__ != "property"
                and not hasattr(getattr(obj, attr), "__fe_strng_mtch__")
            ):
                type_annotations: dict[str, Any] = getattr(cls_, attr).__annotations__
                return len([i for i in type_annotations if i != "return"]) > 0
            return False

        x: T = object.__new__(cls_)
        for cls_func in dir(x):
            if cls_func not in exclude_builtins and add_match_typing(x, cls_func):
                setattr(
                    x,
                    cls_func,
                    MethodType(
                        typing_func(
                            getattr(x, cls_func),
                            excep_raise=excep_raise,
                            cache_size=cache_size,
                            subclass=True,
                            severity=severity,
                        ),
                        x,
                    ),
                )
        return x

    return new_with_match_typing


def install_st_m() -> None:
    import os

    try:
        from strongtyping_modules.install import install  # type: ignore
    except ImportError:
        os.environ["ST_MODULES_INSTALLED"] = "0"
    else:
        if not bool(int(os.environ.get("ST_MODULES_INSTALLED", "0"))):
            logger.info("strongtyping_modules will be installed")
            install()
            os.environ["ST_MODULES_INSTALLED"] = "1"


def action(f: Callable[..., Any], frefs: str, type_function: Any) -> Any:
    """
    This code is original from Ruud van der Ham https://github.com/salabim/easy_property
    """
    _action: Any = action
    if f.__qualname__ == _action.qualname:
        if any(_action.f[fref] is not None for fref in frefs.split("_")):
            raise AttributeError("decorator defined twice")
    else:
        _action.f.update({}.fromkeys(_action.f, None))  # reset all values to None
        _action.qualname = f.__qualname__
    _action.f.update({}.fromkeys(frefs.split("_"), f))  # set all frefs values to f

    # this line was added by myself
    _action.f["setter"] = (
        type_function(_action.f["setter"]) if _action.f["setter"] is not None else None
    )

    return property(
        *(
            _action.f[ref] if (ref != "documenter" or _action.f[ref] is None) else _action.f[ref](0)
            for ref in _action.f
        )
    )


action.qualname = None  # type: ignore
action.f = dict.fromkeys(["getter", "setter", "deleter", "documenter"], None)  # type: ignore
