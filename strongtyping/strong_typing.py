#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 28.04.20
@author: felix
"""
import functools
import inspect
from itertools import zip_longest
import typing

from strongtyping.cached_set import CachedSet


class TypeMisMatch(AttributeError):
    def __init__(self, message):
        super().__init__()
        print(message)


def get_typing_base_class():
    return typing._GenericAlias if hasattr(typing, '_GenericAlias') else typing.GenericMeta


def check_type(argument, type_of):
    check_result = True
    if type_of is not None:
        if isinstance(type_of, get_typing_base_class()):
            if hasattr(type_of, '__origin__'):
                possible_types = type_of.__args__
                origin = type_of.__origin__ if type_of.__origin__ is not None else type_of.__orig_bases__
                if possible_types is not None:
                    check_result = isinstance(argument, origin) and all(check_type(arg, typ) for arg, typ in
                                                                        zip_longest(argument, possible_types,
                                                                                    fillvalue=possible_types[0])) and (
                                               len(argument) == len(type_of.__args__) or (isinstance(argument, list)))
                else:
                    check_result = isinstance(argument, origin[:1])
            else:
                check_result = isinstance(argument, type_of.__args__)
        elif isinstance(type_of, str):
            check_result = argument.__class__.__name__ == type_of
        else:
            try:
                check_result = isinstance(argument, type_of)
            except TypeError:
                check_result = isinstance(argument, type_of._subs_tree()[1:])
    return check_result


def match_typing(_func=None, *, excep_raise: Exception = TypeMisMatch):
    cached_set = CachedSet()

    def wrapper(func):

        @functools.wraps(func)
        def inner(*args, **kwargs):

            # check if func with args and kwargs was checked once before with positive result
            cached_key = (func, repr(args), repr(kwargs))
            if cached_key in cached_set:
                return func(*args, **kwargs)

            # check if a class method is decorated or a 'normal' function
            is_class_function = hasattr(args[0], '__weakref__') if len(args) > 0 else False

            parameter_types = func.__annotations__

            # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
            check_args = all(
                check_type(arg, None if parameter.annotation == inspect._empty else parameter.annotation) for
                arg, parameter in zip(args, inspect.signature(func).parameters.values()))

            check_kwargs = all(check_type(val, parameter_types.get(key)) for key, val in kwargs.items())

            if check_kwargs and check_args:
                cached_set.add(cached_key)
                args = [args[0], *args[1:]] if is_class_function else args
                return func(*args, **kwargs)
            else:
                params = [f'{key}: {val}' for key, val in parameter_types.items() if key != 'return']
                msg = f'Parameters must have following type: {";".join(params)}'
                try:
                    raise excep_raise(message=msg)
                except TypeError:
                    raise excep_raise

        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper
