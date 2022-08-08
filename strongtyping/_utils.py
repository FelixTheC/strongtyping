#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 20.07.20
@author: felix
"""
import inspect
import logging
import os
from types import MethodType
from typing import Any, Type, Union

from strongtyping.config import SEVERITY_LEVEL

logger = logging.getLogger(__name__)

ORIGINAL_DUCK_TYPES = {
    int: [int, float, complex],
    float: [float, complex],
    bytearray: [bytearray, bytes],
}


def remove_subclass(args, subclass):
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


def _severity_level(severity_: Union[str, SEVERITY_LEVEL]):
    if severity_ == "env":
        _level = os.environ.get("ST_SEVERITY", "1")
        try:
            return int(_level)
        except (TypeError, ValueError):
            return SEVERITY_CONFIG[_level].value
    else:
        return severity_.value  # type: ignore


exclude_builtins = dir(object)


def _get_new(
    typing_func, excep_raise: Type[Exception] = TypeError, cache_size=0, severity="env", **kwargs
):
    def new_with_match_typing(cls_, *args, **kwargs):
        def add_match_typing(obj: object, attr: str) -> bool:
            if (
                hasattr(getattr(cls_, attr), "__annotations__")
                and getattr(cls_, attr).__class__.__name__ != "property"
                and not hasattr(getattr(x, attr), "__fe_strng_mtch__")
            ):
                type_annotations = getattr(getattr(cls_, attr), "__annotations__")
                return len([i for i in type_annotations.keys() if i != "return"]) > 0
            return False

        x = object.__new__(cls_)
        [
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
            for cls_func in dir(x)
            if cls_func not in exclude_builtins and add_match_typing(x, cls_func)
        ]
        return x

    return new_with_match_typing


def install_st_m():
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


def action(f, frefs, type_function):  # type: ignore
    """
    This code is original from Ruud van der Ham https://github.com/salabim/easy_property
    """
    if f.__qualname__ == action.qualname:
        if any(action.f[fref] is not None for fref in frefs.split("_")):
            raise AttributeError(f"decorator defined twice")
    else:
        action.f.update({}.fromkeys(action.f, None))  # reset all values to None
        action.qualname = f.__qualname__
    action.f.update({}.fromkeys(frefs.split("_"), f))  # set all frefs values to f

    # this line was added by myself
    action.f["setter"] = (
        type_function(action.f["setter"]) if action.f["setter"] is not None else None
    )

    return property(
        *(
            action.f[ref] if (ref != "documenter" or action.f[ref] is None) else action.f[ref](0)
            for ref in action.f
        )
    )


action.qualname = None  # type: ignore
action.f = dict.fromkeys(["getter", "setter", "deleter", "documenter"], None)  # type: ignore
