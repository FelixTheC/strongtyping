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

from cached_set import CachedSet


class TypeMisMatch(AttributeError):
    def __init__(self, message):
        super().__init__()
        print(message)


typing_base_class = typing._GenericAlias if hasattr(typing, '_GenericAlias') else typing.GenericMeta


def get_possible_types(typ_to_check) -> typing.Union[tuple, None]:
    typ_check_args = typ_to_check.__args__
    if typ_check_args is not None:
        return tuple(typ for typ in typ_check_args if not isinstance(typ, typing.TypeVar))


def get_fillvalue(typ_to_check: any, return_val: any) -> typing.Union[str, int, None]:
    if hasattr(typ_to_check, '_name'):
        return return_val if typ_to_check._name == 'List' else None


def get_origins(typ_to_check: any) -> tuple:
    origin = typ_to_check.__origin__ if typ_to_check.__origin__ is not None else typ_to_check.__orig_bases__
    return origin, origin._name if hasattr(origin, '_name') else ''


def check_type(argument, type_of):
    check_result = True
    if type_of is not None:
        if isinstance(type_of, typing_base_class):
            if hasattr(type_of, '__origin__'):
                possible_types = get_possible_types(type_of)
                origin, origin_name = get_origins(type_of)

                if possible_types and origin_name != 'Union':
                    fillvalue = get_fillvalue(type_of, possible_types[0])
                    check_result = isinstance(argument, origin) and all(check_type(arg, typ) for arg, typ in
                                                                        zip_longest(argument, possible_types,
                                                                                    fillvalue=fillvalue)) and (
                                               len(argument) == len(type_of.__args__) or (isinstance(argument, list)))
                elif origin_name == 'Union':
                    try:
                        check_result = isinstance(argument, possible_types)
                    except TypeError:
                        all(check_type(argument, typ) for typ in possible_types)
                else:
                    possible_type = origin[0] if isinstance(origin, (list, tuple)) else origin
                    check_result = isinstance(argument, possible_type)
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


def match_typing(_func=None, *, excep_raise: Exception = TypeMisMatch, cache_size=0):
    cached_set = CachedSet(cache_size) if cache_size > 0 else None

    def wrapper(func):
        arg_names = [name for name in inspect.signature(func).parameters]
        annotations = func.__annotations__

        @functools.wraps(func)
        def inner(*args, **kwargs):

            if cached_set is not None:
                # check if func with args and kwargs was checked once before with positive result
                cached_key = (func, repr(args), repr(kwargs))
                if cached_key in cached_set:
                    return func(*args, **kwargs)

            # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
            failed_arg_names = tuple(
                arg_name for arg, arg_name in zip(args, arg_names) if not check_type(arg, annotations.get(arg_name))
            )
            failed_kwarg_names = tuple(
                kwarg_name for kwarg_name, kwarg in kwargs.items() if not check_type(kwarg, annotations.get(kwarg_name))
            )

            if failed_arg_names or failed_kwarg_names:
                params = [f"{name}: {annotations[name]}" for name in failed_arg_names + failed_kwarg_names]
                msg = f'Incorrect parameters: {", ".join(params)}'
                raise excep_raise(msg)

            if cached_set is not None:
                cached_set.add(cached_key)

            return func(*args, **kwargs)

        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper
