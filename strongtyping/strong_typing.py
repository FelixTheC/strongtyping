#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 28.04.20
@author: felix
"""
import inspect
from functools import wraps
import warnings

from strongtyping.strong_typing_utils import TypeMisMatch
from strongtyping.strong_typing_utils import check_type

from strongtyping._utils import action
from strongtyping._utils import _get_new
from strongtyping._utils import _severity_level
from strongtyping._utils import remove_subclass
from strongtyping.cached_set import CachedSet


def match_typing(_func=None, *, excep_raise: Exception = TypeMisMatch, cache_size=0,
                 subclass: bool = False, severity='env', **kwargs):
    cached_set = None if cache_size == 0 else CachedSet(cache_size)

    def wrapper(func):
        # needed in py 3.10
        # globals().update(func.__globals__)

        arg_names = [name for name in inspect.signature(func).parameters]
        annotations = func.__annotations__

        severity_level = _severity_level(severity)

        @wraps(func)
        def inner(*args, **kwargs):
            if arg_names and severity_level > 0:

                args = remove_subclass(args, subclass)

                if cached_set is not None:
                    # check if func with args and kwargs was checked once before with positive result
                    cached_key = (func, args.__str__(), kwargs.__str__())
                    if cached_key in cached_set:
                        return func(*args, **kwargs)

                # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
                failed_params = tuple(
                    arg_name for arg, arg_name in zip(args, arg_names) if not check_type(arg, annotations.get(arg_name))
                )
                failed_params += tuple(
                    kwarg_name for kwarg_name, kwarg in kwargs.items() if not check_type(kwarg,
                                                                                         annotations.get(kwarg_name))
                )

                if failed_params:
                    msg = f'Incorrect parameters: {", ".join(f"{name}: {annotations[name]}" for name in failed_params)}'

                    if excep_raise is not None and severity_level == 1:
                        raise excep_raise(msg)
                    else:
                        warnings.warn(msg, RuntimeWarning)

                if cached_set is not None:
                    cached_set.add(cached_key)
            return func(*args, **kwargs)

        inner.__fe_strng_mtch__ = 0
        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper


def match_class_typing(_cls=None, *, excep_raise: Exception = TypeError, cache_size=0, severity='env', **kwargs):

    def wrapper(cls):

        severity_level = _severity_level(severity)
        if severity_level > 0:
            cls.__new__ = _get_new(match_typing, excep_raise, cache_size, severity, **kwargs)
            if hasattr(cls.__init__, '__annotations__'):
                cls.__init__ = match_typing(cls.__init__)
        return cls

    if _cls is not None:
        return wrapper(_cls)
    else:
        return wrapper


def getter(func):
    return action(func, 'getter', match_typing)


def setter(func):
    return action(func, 'setter', match_typing)


def getter_setter(func):
    return action(func, 'getter_setter', match_typing)
