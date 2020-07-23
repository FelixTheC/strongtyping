#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 20.07.20
@author: felix
"""
import os
from types import MethodType
from typing import Union

from strongtyping.config import SEVERITY_LEVEL


def remove_subclass(args, subclass):
    cls = args[0] if subclass else None
    if cls is not None:
        args = args[1:]
    return args


SEVERITY_CONFIG = {
    'warning': SEVERITY_LEVEL.WARNING,
    'disable': SEVERITY_LEVEL.DISABLED,
    'enable': SEVERITY_LEVEL.ENABLED
}


def _severity_level(severity_: Union[str, SEVERITY_LEVEL]):
    if severity_ == 'env':
        _level = os.environ.get('ST_SEVERITY', 1)
        try:
            return int(_level)
        except (TypeError, ValueError):
            return SEVERITY_CONFIG[_level].value
    else:
        return severity_.value


exclude_builtins = dir(object)


def _get_new(typing_func, excep_raise: Exception = TypeError, cache_size=0, severity='env', **kwargs):

    def new_with_match_typing(cls_, *args, **kwargs):
        x = object.__new__(cls_)
        [setattr(x, cls_func, MethodType(typing_func(getattr(x, cls_func),
                                                     excep_raise=excep_raise,
                                                     cache_size=cache_size,
                                                     subclass=True,
                                                     severity=severity), x)
                 ) for cls_func in dir(x)
         if cls_func not in exclude_builtins and
         hasattr(getattr(x, cls_func), '__annotations__') and
         getattr(getattr(x, cls_func), '__annotations__') and
         not hasattr(getattr(x, cls_func), '__fe_strng_mtch__')]
        return x

    return new_with_match_typing


def action(f, frefs, type_function):
    """
    This code is original from Ruud van der Ham https://github.com/salabim/easy_property
    """
    if f.__qualname__ == action.qualname:
        if any(action.f[fref] is not None for fref in frefs.split("_")):
            raise AttributeError(f"decorator defined twice")
    else:
        action.f.update({}.fromkeys(action.f, None))  # reset all values to None
        action.qualname = f.__qualname__
    action.f.update({}.fromkeys(frefs.split('_'), f))  # set all frefs values to f

    # this line was added by myself
    action.f['setter'] = type_function(action.f['setter']) if action.f['setter'] is not None else None

    return property(*(action.f[ref] if (ref != "documenter" or action.f[ref] is None)
                      else action.f[ref](0) for ref in action.f))


action.qualname = None
action.f = dict.fromkeys(["getter", "setter", "deleter", "documenter"], None)
